"""
new_csv.py - Bước 1 của quy trình K-Means: tính 4 đặc trưng cho mọi mã và xuất ra CSV.

Đầu vào : stock_cleaned.csv (cùng thư mục)
Đầu ra  : D:/DATA/stock_features.csv
          gồm các cột Ticker, CAGR, Annualized_Volatility, Max_Drawdown, Sharpe_Ratio

Lưu ý: bước tiếp theo (check_new_csv.py) đọc stock_features.csv trong thư mục
K_means, không phải trong D:/DATA. Cần chép file sang (xem README) hoặc sửa OUTPUT_FILE.
"""
import pandas as pd
from pathlib import Path

# Import các hàm tính đặc trưng từ file feature.py (cùng thư mục).
# Lưu ý: khi import, feature.py cũng tự đọc stock_cleaned.csv ở cấp module.
from feature import (
    filter_stocks,
    annualized_return,
    annualized_volatility,
    maximum_drawdown,
    sharpe_ratio
)

# Đường dẫn file đầu vào và đầu ra
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "stock_cleaned.csv"
OUTPUT_FILE = Path("D:/DATA/stock_features.csv")  # Đường dẫn tuyệt đối, chỉ dùng được trên máy có ổ D


def export_features():
    """Tính 4 đặc trưng cho toàn bộ cổ phiếu hợp lệ và ghi ra OUTPUT_FILE."""

    # 1. Đọc dữ liệu giá
    df = pd.read_csv(INPUT_FILE)

    # 2. Chuyển cột Date sang kiểu datetime và sắp xếp theo mã, ngày
    #    (các hàm tính đặc trưng cần dữ liệu đúng thứ tự thời gian)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(["Ticker", "Date"])

    # 3. Lọc cổ phiếu: ít nhất 252 phiên và còn giao dịch ở ngày mới nhất
    df = filter_stocks(df, min_sessions=252)

    # 4. Tính các đặc trưng, sau đó ghép lần lượt vào bảng CAGR theo Ticker
    features = annualized_return(df)

    volatility = annualized_volatility(df)
    features = features.merge(volatility, on="Ticker", how="left")

    mdd = maximum_drawdown(df)
    features = features.merge(mdd, on="Ticker", how="left")

    sharpe = sharpe_ratio(df)
    features = features.merge(sharpe, on="Ticker", how="left")

    # 5. Chỉ giữ mã cổ phiếu và 4 đặc trưng dùng cho K-Means
    #    (bỏ các cột trung gian như first_price, last_price, years, ...)
    features = features[[
        "Ticker",
        "CAGR",
        "Annualized_Volatility",
        "Max_Drawdown",
        "Sharpe_Ratio"
    ]]

    # 6. Tạo thư mục đầu ra nếu chưa có
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 7. Xuất file CSV (utf-8-sig để Excel mở không lỗi font)
    features.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("Đã xuất file CSV thành công!")
    print(f"Đường dẫn: {OUTPUT_FILE}")
    print(f"Số cổ phiếu: {len(features)}")


if __name__ == "__main__":
    export_features()
