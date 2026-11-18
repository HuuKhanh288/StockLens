# Feature: Annualized Return (CAGR)
import pandas as pd
from pathlib import Path

# Đọc dữ liệu
BASE_DIR = Path(__file__).resolve().parent.parent
df = pd.read_csv(BASE_DIR / "data" / "stock_cleaned.csv")

# Chuẩn hóa dữ liệu
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values(["Ticker", "Date"])


def annualized_return(df):

    # Lấy giá và ngày đầu kỳ, cuối kỳ của từng cổ phiếu
    result = df.groupby("Ticker").agg(
        first_price=("Close", "first"),
        last_price=("Close", "last"),
        first_date=("Date", "first"),
        last_date=("Date", "last"),
        n_sessions=("Date", "count")
    )

    # Tính thời gian nắm giữ (năm)
    result["years"] = (
        result["last_date"] - result["first_date"]
    ).dt.days / 365.25

    # Loại dữ liệu không hợp lệ
    result = result[
        (result["n_sessions"] >= 2)
        & (result["first_price"] > 0)
        & (result["last_price"] > 0)
        & (result["years"] > 0)
    ].copy()

    # Tính CAGR
    result["CAGR"] = (
        (result["last_price"] / result["first_price"])
        ** (1 / result["years"]) - 1
    )

    return result.reset_index()


if __name__ == "__main__":

    ticker = input("Nhập mã cổ phiếu: ").strip().upper()

    features = annualized_return(df)
    stock = features[features["Ticker"] == ticker]

    if stock.empty:
        print(f"Không tìm thấy mã {ticker}!")
    else:
        s = stock.iloc[0]

        # Giả sử mua 1000 cổ phiếu
        quantity = 1000

        # Giá trị khoản đầu tư
        initial_value = quantity * s["first_price"]
        final_value = initial_value * (1 + s["CAGR"]) ** s["years"]

        print(f"\n========== {ticker} ==========")
        print(f"Ngày mua: {s['first_date']:%d/%m/%Y}")
        print(f"Giá mua (Close): {s['first_price']:,.2f}")

        print(f"Ngày cuối cùng: {s['last_date']:%d/%m/%Y}")
        print(f"Giá cuối kỳ (Close): {s['last_price']:,.2f}")

        print(f"Thời gian nắm giữ: {s['years']:.2f} năm")
        print(f"CAGR: {s['CAGR']:.2%}")

        print(f"\nGiá trị ban đầu (1000 CP): {initial_value:,.2f}")
        print(f"Giá trị hiện tại (1000 CP): {final_value:,.2f}")
        print(f"Lãi/Lỗ: {final_value - initial_value:+,.2f}")   

# Volatility: Độ biến động của tỷ suất sinh lời trong 1 khoảng thời gian
# Volatility cao: Tỷ suất sinh lời biến động mạnh, cổ phiếu có mức độ rủi ro biến động giá cao.
# Volatility thấp: Tỷ suất sinh lời ít biến động, cổ phiếu có mức độ ổn định giá cao hơn.
