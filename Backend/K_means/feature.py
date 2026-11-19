# Feature: Annualized Return (CAGR) - tỷ suất sinh lời kép trung bình của cổ phiếu 
import pandas as pd
from pathlib import Path
import numpy as np

# Đọc dữ liệu
BASE_DIR = Path(__file__).resolve().parent
df = pd.read_csv(BASE_DIR / "stock_cleaned.csv")

# Chuẩn hóa dữ liệu
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values(["Ticker", "Date"])

## LỌC CỔ PHIẾU CÓ ÍT NHẤT 252 PHIÊN GIAO DỊCH và không lấy cổ phiếu hủy niêm yết

def filter_stocks(df, min_sessions=252):

    # Ngày mới nhất của toàn bộ dữ liệu
    latest_date = df["Date"].max()

    # Thống kê số dòng và ngày cuối cùng của từng cổ phiếu
    stock_info = df.groupby("Ticker").agg(
        n_sessions=("Date", "size"),
        last_date=("Date", "max")
    )

    # Lấy những cổ phiếu thỏa mãn cả 2 điều kiện
    valid_tickers = stock_info[
        (stock_info["n_sessions"] >= min_sessions)
        & (stock_info["last_date"] == latest_date)
    ].index

    # Lọc dữ liệu
    return df[df["Ticker"].isin(valid_tickers)].copy()


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

# Volatility: Độ biến động của tỷ suất sinh lời trong 1 khoảng thời gian
# Volatility cao: Tỷ suất sinh lời biến động mạnh, cổ phiếu có mức độ rủi ro biến động giá cao.
# Volatility thấp: Tỷ suất sinh lời ít biến động, cổ phiếu có mức độ ổn định giá cao hơn.

# Feature: Annualized Volatility
# Đo độ biến động của tỷ suất sinh lời hằng ngày, quy đổi về năm

def annualized_volatility(df):

    # Tạo bản sao để không thay đổi dữ liệu gốc
    df = df.copy()

    # Tính tỷ suất sinh lời hằng ngày của từng cổ phiếu
    df["Daily_Return"] = df.groupby("Ticker")["Close"].pct_change()

    # Tính độ lệch chuẩn tỷ suất sinh lời hằng ngày
    result = df.groupby("Ticker")["Daily_Return"].std()

    # Quy đổi Volatility về năm
    result = result * np.sqrt(252)

    # Đặt tên feature
    result.name = "Annualized_Volatility"

    return result.reset_index()

# TÍNH MAXIMUM DRAWDOWN
def maximum_drawdown(df):
    # Tạo bản sao dữ liệu để tính toán
    data = df.copy()

    # Sắp xếp dữ liệu theo mã cổ phiếu và thời gian
    data = data.sort_values(["Ticker", "Date"])

    # Tìm đỉnh giá đóng cửa lũy kế của từng cổ phiếu
    data["Peak"] = data.groupby("Ticker")["Close"].cummax()

    # Tính Drawdown tại từng phiên
    data["Drawdown"] = (data["Close"] - data["Peak"]) / data["Peak"]

    # Lấy mức sụt giảm lớn nhất của từng cổ phiếu
    mdd = (
        data.groupby("Ticker")["Drawdown"]
        .min()
        .reset_index(name="Max_Drawdown")
    )

    return mdd

# FEATURE 4: SHARPE RATIO
# Đánh giá lợi nhuận vượt mức phi rủi ro trên mỗi đơn vị rủi ro

def sharpe_ratio(df, risk_free_rate=0.04):

    # Tạo bản sao dữ liệu
    data = df.copy()

    # Tính tỷ suất sinh lời hằng ngày
    data["Daily_Return"] = data.groupby("Ticker")["Close"].pct_change()

    # Tính tỷ suất sinh lời trung bình ngày của từng cổ phiếu
    mean_return = data.groupby("Ticker")["Daily_Return"].mean()

    # Tính độ lệch chuẩn tỷ suất sinh lời ngày
    std_return = data.groupby("Ticker")["Daily_Return"].std()

    # Quy đổi lợi nhuận trung bình về năm
    annual_return = mean_return * 252

    # Quy đổi Volatility về năm
    annual_volatility = std_return * np.sqrt(252)

    # Tính Sharpe Ratio
    sharpe = (annual_return - risk_free_rate) / annual_volatility

    # Xử lý trường hợp Volatility bằng 0
    sharpe = sharpe.replace([np.inf, -np.inf], np.nan)

    # Đặt tên Feature
    sharpe.name = "Sharpe_Ratio"

    return sharpe.reset_index()

if __name__ == "__main__":

    ticker = input("Nhập mã cổ phiếu: ").strip().upper()
    #Lọc cổ phiếu   
    df = filter_stocks(df, min_sessions=252)

    print(f"Số cổ phiếu đủ điều kiện: {df['Ticker'].nunique()}")

    # 1. Tính CAGR cho toàn bộ cổ phiếu
    features = annualized_return(df)

    # 2. Tính Volatility cho toàn bộ cổ phiếu
    volatility = annualized_volatility(df)

    # Ghép Volatility vào bảng features
    features = features.merge(volatility, on="Ticker", how="left")

    # 3. Tính Maximum Drawdown cho toàn bộ cổ phiếu
    mdd = maximum_drawdown(df)

    # Ghép Maximum Drawdown vào bảng features
    features = features.merge(mdd, on="Ticker", how="left")

    # 4. Tính Sharpe Ratio cho toàn bộ cổ phiếu
    sharpe = sharpe_ratio(df)

    # Ghép Sharpe Ratio vào bảng features
    features = features.merge(sharpe, on="Ticker", how="left")


    # 4. Lựa chọn cổ phiếu muốn xem
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

        # Hiển thị các Feature
        print(f"CAGR: {s['CAGR']:.2%}")
        print(f"Annualized Volatility: {s['Annualized_Volatility']:.2%}")
        print(f"Maximum Drawdown: {s['Max_Drawdown']:.2%}")
        print(f"Sharpe Ratio: {s['Sharpe_Ratio']:.2f}")

        print(f"\nGiá trị ban đầu (1000 CP): {initial_value:,.2f}")
        print(f"Giá trị hiện tại (1000 CP): {final_value:,.2f}")
        print(f"Lãi/Lỗ: {final_value - initial_value:+,.2f}")

    