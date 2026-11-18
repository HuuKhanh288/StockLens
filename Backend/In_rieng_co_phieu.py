import pandas as pd
from pathlib import Path

# 1. Đường dẫn dữ liệu đã xử lý
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "stock_cleaned.csv"

# 2. Đọc dữ liệu
df = pd.read_csv(DATA_PATH)

# 3. Nhập mã cổ phiếu
ticker = input("Nhập mã cổ phiếu: ").strip().upper()

# 4. Lấy dữ liệu cổ phiếu
stock = df[df["Ticker"] == ticker].copy()

if stock.empty:
    print(f"Không tìm thấy mã {ticker}!")

else:
    # 5. Chuẩn hóa ngày
    stock["Date"] = pd.to_datetime(
        stock["Date"],
        format="%Y-%m-%d",
        errors="coerce"
    )

    # 6. Sắp xếp dữ liệu theo thời gian
    stock = stock.dropna(subset=["Date"])
    stock = stock.sort_values("Date")

    if stock.empty:
        print(f"Mã {ticker} không có ngày giao dịch hợp lệ!")

    else:
        # 7. Menu lựa chọn
        print("\n========== LỰA CHỌN ==========")
        print("1. In 300 phiên giao dịch gần nhất")
        print("2. In phiên đầu tiên và phiên cuối cùng")

        choice = input("\nNhập lựa chọn (1 hoặc 2): ").strip()

        if choice == "1":

            # Lấy 300 phiên gần nhất
            result = stock.tail(300)

            print(f"\n========== {ticker} - 300 PHIÊN ==========\n")
            print(result.to_string(index=False))

            print(f"\nTổng số phiên: {len(result)}")
            print(f"Phiên đầu tiên: {result['Date'].min().date()}")
            print(f"Phiên cuối cùng: {result['Date'].max().date()}")

        elif choice == "2":

            # Lấy phiên đầu tiên và cuối cùng của toàn bộ dữ liệu
            result = pd.concat([
                stock.head(1),
                stock.tail(1)
            ]).drop_duplicates()

            print(f"\n========== {ticker} - ĐẦU KỲ VÀ CUỐI KỲ ==========\n")
            print(result.to_string(index=False))

            print(f"\nTổng số phiên trong dữ liệu: {len(stock)}")
            print(f"Phiên đầu tiên: {stock['Date'].min().date()}")
            print(f"Phiên cuối cùng: {stock['Date'].max().date()}")

        else:
            print("Lựa chọn không hợp lệ!")