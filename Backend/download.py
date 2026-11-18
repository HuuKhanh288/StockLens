from pathlib import Path
import shutil

# Thư mục dự án StockLens
BASE_DIR = Path(__file__).resolve().parent.parent

# File CSV đã xử lý
DATA_PATH = BASE_DIR / "data" / "stock_cleaned.csv"

# Thư mục DATA trên ổ D
DOWNLOAD_DIR = Path("D:/DATA")


def download_csv():
    if not DATA_PATH.exists():
        print("Không tìm thấy file stock_cleaned.csv!")
        return

    # Tạo thư mục nếu chưa tồn tại
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Đường dẫn lưu file
    output_path = DOWNLOAD_DIR / "stock_cleaned.csv"

    # Sao chép CSV sang thư mục DATA
    shutil.copy2(DATA_PATH, output_path)

    print("Đã xuất file CSV thành công!")
    print(f"Đường dẫn: {output_path}")


if __name__ == "__main__":
    download_csv()