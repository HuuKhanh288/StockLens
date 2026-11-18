"""StockLens Journal — offline, dependency-free API + SQLite persistence.
Run: python server.py and open http://127.0.0.1:8765
"""
from __future__ import annotations

import json
import re
import sqlite3
import threading
import webbrowser
from datetime import date, datetime
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "stocklens.sqlite3"
HOST = "127.0.0.1"  # Local-only: not exposed to other devices
PORT = 8765
STATUSES = {"watch", "done", "setup", "fail", "success", "forming"}
TICKER_PATTERN = re.compile(r"^[A-Z0-9._-]{1,12}$")
ALLOWED_FILES = {
    "/", "/index.html", "/css/shell.css", "/css/journal.css",
    "/css/stocklens.css", "/js/main.js", "/js/app.js",
    "/js/stocklens.js", "/favicon.svg",
}


SAMPLE_ENTRIES = [
    ("2026-11-05", "BVB", "Có phân kỳ tam đoạn: quan sát nếu mua ngày 04/11 thì thế nào?", "watch"),
    ("2026-11-05", "LPB", "Quan sát cây hàng về ngày 04/11.", "watch"),
    ("2026-11-05", "BSR", "Quan sát phản ứng tại nền giá.", "watch"),
    ("2026-11-05", "POW", "Quan sát cây hàng về 04/11: nghi ngờ rũ bỏ + phân kỳ dương, nhưng tín hiệu xác nhận chưa rõ ràng.", "watch"),
    ("2026-11-05", "FIT", "Quan sát vận động của FIT trong phiên hàng về ngày 04/11.", "watch"),
    ("2026-11-05", "JVC", "Giá trên mây Ichimoku và trên dao găm.", "setup"),
]


def connect():
    con = sqlite3.connect(DB_PATH, timeout=15)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA busy_timeout=15000")
    return con


def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        db.execute("""CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            watch_date TEXT NOT NULL,
            ticker TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'watch' CHECK(status IN ('watch','done','setup','fail','success','forming')),
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            UNIQUE(watch_date, ticker)
        )""")
        # Cơ sở dữ liệu cũ giới hạn 3 trạng thái bằng CHECK constraint.
        # SQLite không hỗ trợ ALTER COLUMN CHECK: thay bảng trong transaction,
        # giữ nguyên id, dữ liệu và thời gian của toàn bộ ghi chép cũ.
        schema = db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='entries'").fetchone()[0]
        if "'forming'" not in schema:
            db.execute("""CREATE TABLE entries_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                watch_date TEXT NOT NULL,
                ticker TEXT NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'watch'
                    CHECK(status IN ('watch','done','setup','fail','success','forming')),
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                UNIQUE(watch_date, ticker)
            )""")
            db.execute("""INSERT INTO entries_new (id,watch_date,ticker,note,status,created_at,updated_at)
                SELECT id,watch_date,ticker,note,status,created_at,updated_at FROM entries""")
            db.execute("DROP TABLE entries")
            db.execute("ALTER TABLE entries_new RENAME TO entries")
        db.execute("CREATE INDEX IF NOT EXISTS idx_entries_date ON entries(watch_date DESC)")
        if db.execute("SELECT COUNT(*) FROM entries").fetchone()[0] == 0:
            # Only seed on a genuinely new database; if the user deletes all rows,
            # restarting the application must not repopulate sample data.
            seeded = db.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='metadata'").fetchone()[0]
            if not seeded:
                db.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
                db.execute("INSERT INTO metadata(key,value) VALUES('initialized','yes')")
                db.executemany("INSERT INTO entries(watch_date,ticker,note,status) VALUES(?,?,?,?)", SAMPLE_ENTRIES)
        else:
            db.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            db.execute("INSERT OR IGNORE INTO metadata(key,value) VALUES('initialized','yes')")


def now_str():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def checked_entry(data, *, partial=False):
    if not isinstance(data, dict):
        raise ValueError("Dữ liệu phải là một đối tượng JSON.")
    fields = {}
    if "watch_date" in data or not partial:
        val = data.get("watch_date")
        if not isinstance(val, str):
            raise ValueError("Ngày ghi chép không hợp lệ.")
        try:
            parsed = date.fromisoformat(val)
        except ValueError as exc:
            raise ValueError("Ngày phải theo định dạng YYYY-MM-DD.") from exc
        if parsed.isoformat() != val:
            raise ValueError("Ngày phải theo định dạng YYYY-MM-DD.")
        fields["watch_date"] = val
    if "ticker" in data or not partial:
        ticker = data.get("ticker")
        if not isinstance(ticker, str):
            raise ValueError("Hãy nhập mã cổ phiếu.")
        ticker = ticker.strip().upper()
        if not TICKER_PATTERN.fullmatch(ticker):
            raise ValueError("Mã cổ phiếu chỉ gồm 1–12 ký tự A–Z, 0–9, dấu chấm, gạch ngang hoặc gạch dưới.")
        fields["ticker"] = ticker
    if "note" in data or not partial:
        note = data.get("note", "")
        if not isinstance(note, str) or len(note) > 10000:
            raise ValueError("Nội dung theo dõi tối đa 10.000 ký tự.")
        fields["note"] = note
    if "status" in data or not partial:
        status = data.get("status", "watch")
        if status not in STATUSES:
            raise ValueError("Tiêu chí không hợp lệ.")
        fields["status"] = status
    if not fields:
        raise ValueError("Không có trường dữ liệu nào cần cập nhật.")
    return fields


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def json_response(self, data, status=200):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def read_json(self):
        try:
             length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("Kích thước yêu cầu không hợp lệ.") from exc
        if not 0 < length <= 8 * 1024 * 1024:
            raise ValueError("Dữ liệu trống hoặc lớn hơn 8 MB.")
        try:
            return json.loads(self.rfile.read(length))
        except (ValueError, UnicodeDecodeError) as exc:
            raise ValueError("Tệp JSON không hợp lệ.") from exc

    def route(self, method):
        path = urlsplit(self.path).path
        if path == "/api/health" and method == "GET":
            return self.json_response({"ok": True, "storage": "SQLite", "time": now_str()})
        if path == "/api/entries" and method == "GET":
            with connect() as db:
                rows = db.execute("SELECT * FROM entries ORDER BY watch_date DESC, updated_at DESC, id DESC").fetchall()
                return self.json_response({"entries": [dict(x) for x in rows]})
        if path == "/api/entries" and method == "POST":
            item = checked_entry(self.read_json())
            with connect() as db:
                cur = db.execute("INSERT INTO entries (watch_date,ticker,note,status) VALUES (:watch_date,:ticker,:note,:status)", item)
                row = db.execute("SELECT * FROM entries WHERE id=?", (cur.lastrowid,)).fetchone()
                return self.json_response({"entry": dict(row)}, 201)
        match = re.fullmatch(r"/api/entries/(\d+)", path)
        if match:
            entry_id = int(match.group(1))
            if method == "PATCH":
                patch = checked_entry(self.read_json(), partial=True)
                assigns = ", ".join(f"{field} = ?" for field in patch)
                vals = list(patch.values()) + [entry_id]
                with connect() as db:
                    cur = db.execute(f"UPDATE entries SET {assigns}, updated_at=datetime('now','localtime') WHERE id=?", vals)
                    if not cur.rowcount:
                        return self.json_response({"error": "Không tìm thấy dòng này."}, 404)
                    row = db.execute("SELECT * FROM entries WHERE id=?", (entry_id,)).fetchone()
                    return self.json_response({"entry": dict(row)})
            if method == "DELETE":
                with connect() as db:
                    cur = db.execute("DELETE FROM entries WHERE id=?", (entry_id,))
                    return self.json_response({"deleted": bool(cur.rowcount)}, 200 if cur.rowcount else 404)
        if path == "/api/clone" and method == "POST":
            data = self.read_json()
            target = checked_entry({"watch_date": data.get("target_date"), "ticker": "TEMP"})["watch_date"]
            with connect() as db:
                source = db.execute("SELECT MAX(watch_date) FROM entries WHERE watch_date < ?", (target,)).fetchone()[0]
                if source is None:
                    return self.json_response({"source_date": None, "created": 0})
                source_entries = db.execute("SELECT ticker,note FROM entries WHERE watch_date=?", (source,)).fetchall()
                created = 0
                for row in source_entries:
                    created += db.execute("INSERT OR IGNORE INTO entries(watch_date,ticker,note,status) VALUES(?,?,?,'watch')", (target, row["ticker"], row["note"])).rowcount
                return self.json_response({"source_date": source, "created": created})
        if path == "/api/import" and method == "POST":
            data = self.read_json()
            rows = data.get("entries") if isinstance(data, dict) else data
            if not isinstance(rows, list) or len(rows) > 10000:
                raise ValueError("Tệp sao lưu phải có danh sách entries (tối đa 10.000 dòng).")
            valid = [checked_entry(item) for item in rows]
            with connect() as db:
                created = 0
                for item in valid:
                    created += db.execute("INSERT OR IGNORE INTO entries(watch_date,ticker,note,status) VALUES (:watch_date,:ticker,:note,:status)", item).rowcount
                return self.json_response({"created": created, "skipped": len(valid)-created})
        return self.json_response({"error": "Không tìm thấy API."}, 404)

    def serve_static(self, *, head=False):
        path = urlsplit(self.path).path
        if path not in ALLOWED_FILES:
            return self.send_error(HTTPStatus.NOT_FOUND, "Not found")
        # Explicit aliases keep SQLite and other local files inaccessible.
        if path in ("/journal", "/journal/"):
            self.path = "/journal/index.html"
        elif path in ("/stocklens", "/stocklens/"):
            self.path = "/stocklens/index.html"
        elif path == "/":
            self.path = "/index.html"
        return super().do_HEAD() if head else super().do_GET()

    def do_GET(self):
        if urlsplit(self.path).path.startswith("/api/"):
            return self.handle_api("GET")
        return self.serve_static()

    def do_HEAD(self):
        return self.serve_static(head=True)

    def do_POST(self):
        return self.handle_api("POST")

    def do_PATCH(self):
        return self.handle_api("PATCH")

    def do_DELETE(self):
        return self.handle_api("DELETE")

    def handle_api(self, method):
        try:
            self.route(method)
        except ValueError as exc:
            self.json_response({"error": str(exc)}, 400)
        except sqlite3.IntegrityError as exc:
            if "UNIQUE" in str(exc).upper():
                self.json_response({"error": "Mã cổ phiếu này đã được ghi trong ngày đó."}, 409)
            else:
                self.json_response({"error": "Dữ liệu không hợp lệ."}, 400)
        except sqlite3.Error as exc:
            print("Database error:", exc)
            self.json_response({"error": "Không thể lưu vào cơ sở dữ liệu SQLite."}, 500)
        except Exception as exc:
            print("Unexpected error:", repr(exc))
            self.json_response({"error": "Đã xảy ra lỗi khi xử lý yêu cầu."}, 500)


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == "__main__":
    initialize_database()
    try:
        server = Server((HOST, PORT), Handler)
    except OSError as exc:
        print(f"Không khởi động được cổng {PORT}: {exc}")
        raise SystemExit(1)
    url = f"http://{HOST}:{PORT}"
    print("=" * 60)
    print(" STOCKLENS — TRANG CHỦ VÀ CÁC CHỨC NĂNG")
    print(f" Mở trang: {url}")
    print(f" Dữ liệu lưu tại: {DB_PATH}")
    print(" Đóng cửa sổ này để dừng ứng dụng (dữ liệu vẫn còn).")
    print("=" * 60)
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Đã dừng ứng dụng. Dữ liệu vẫn nằm trong SQLite.")
    finally:
        server.server_close()
