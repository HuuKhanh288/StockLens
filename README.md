# StockLens — Một trang duy nhất (SPA)

Mở `run_windows.bat` trên Windows, hoặc chạy `python server.py` rồi truy cập http://127.0.0.1:8765/.

Menu chuyển giữa **Trang chủ**, **Nhật ký giao dịch**, **Bộ lọc cổ phiếu** mà không chuyển trang.

- `index.html`: chứa cả ba giao diện.
- `css/shell.css`: menu và trang chủ.
- `css/journal.css`: giao diện nhật ký, đã cô lập CSS.
- `css/stocklens.css`: giao diện bộ lọc, đã cô lập CSS.
- `js/main.js`: chuyển giao diện không tải lại trang.
- `js/app.js`: toàn bộ logic nhật ký cũ.
- `js/stocklens.js`: tương tác checkbox/radio; chưa lọc cổ phiếu thực tế.
- `server.py`: API SQLite và web server.
- `data/stocklens.sqlite3`: tự tạo nếu chưa có. **Sao lưu và giữ file cũ** nếu muốn giữ nhật ký hiện tại.

**Quan trọng:** Đóng server cũ trước khi chạy phiên bản mới. Nếu dùng chung cổng 8765, server cũ sẽ khiến bạn nhìn thấy giao diện cũ.
