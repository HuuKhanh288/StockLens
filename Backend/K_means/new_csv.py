import pandas as pd
from pathlib import Path

# Import các hàm từ file features.py
from feature import (
    filter_stocks,
    annualized_return,
    annualized_volatility,
    maximum_drawdown,
    sharpe_ratio
)

# Đường dẫn
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "stock_cleaned.csv"
OUTPUT_FILE = Path("D:/DATA/stock_features.csv")


def export_features():

    # 1. Đọc dữ liệu
    df = pd.read_csv(INPUT_FILE)

    # 2. Chuẩn hóa ngày và sắp xếp dữ liệu
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(["Ticker", "Date"])

    # 3. Lọc cổ phiếu
    df = filter_stocks(df, min_sessions=252)

    # 4. Tính các Feature
    features = annualized_return(df)

    volatility = annualized_volatility(df)
    features = features.merge(volatility, on="Ticker", how="left")

    mdd = maximum_drawdown(df)
    features = features.merge(mdd, on="Ticker", how="left")

    sharpe = sharpe_ratio(df)
    features = features.merge(sharpe, on="Ticker", how="left")

    # 5. Chỉ lấy các Feature cần thiết cho K-Means
    features = features[[
        "Ticker",
        "CAGR",
        "Annualized_Volatility",
        "Max_Drawdown",
        "Sharpe_Ratio"
    ]]

    # 6. Tạo thư mục đầu ra nếu chưa có
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 7. Xuất file CSV
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