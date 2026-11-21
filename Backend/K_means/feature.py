"""
feature.py - Tính 4 đặc trưng tài chính cho từng mã cổ phiếu (dùng cho K-Means).

Các đặc trưng:
    1. CAGR                   : tốc độ tăng trưởng kép hằng năm của giá đóng cửa
    2. Annualized_Volatility  : độ biến động của tỷ suất sinh lời ngày, quy đổi về năm
    3. Max_Drawdown           : mức sụt giảm lớn nhất từ một đỉnh giá (số âm hoặc 0)
    4. Sharpe_Ratio           : lợi nhuận vượt lãi suất phi rủi ro trên mỗi đơn vị biến động

Dữ liệu đầu vào: stock_cleaned.csv (cùng thư mục), cần các cột Ticker, Date, Close.

Cách dùng:
    - Được import bởi new_csv.py để xuất file đặc trưng cho toàn bộ cổ phiếu.
    - Chạy trực tiếp `python feature.py` để nhập một mã và xem các chỉ số trên terminal.

Lưu ý: file CSV được đọc ngay ở cấp module, nên mỗi lần `import feature`
(ví dụ trong new_csv.py) cũng sẽ đọc stock_cleaned.csv một lần.
"""
import pandas as pd
from pathlib import Path
import numpy as np

# Đọc dữ liệu giá từ stock_cleaned.csv nằm cùng thư mục với file này
BASE_DIR = Path(__file__).resolve().parent
df = pd.read_csv(BASE_DIR / "stock_cleaned.csv")

# Chuyển cột Date sang kiểu datetime và sắp xếp theo mã, ngày tăng dần.
# Thứ tự này bắt buộc vì các hàm bên dưới dùng "first"/"last", pct_change()
# và cummax(), đều phụ thuộc vào thứ tự thời gian.
# (Đây chỉ là chuẩn bị dữ liệu, KHÔNG phải chuẩn hóa giá trị.)
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values(["Ticker", "Date"])


# ==================================================
# LỌC CỔ PHIẾU
# ==================================================

def filter_stocks(df, min_sessions=252):
    """
    Giữ lại các mã thỏa mãn đồng thời 2 điều kiện:
        - Có ít nhất `min_sessions` dòng dữ liệu (252 ≈ số phiên giao dịch trong 1 năm).
        - Có giao dịch vào ngày mới nhất của toàn bộ dữ liệu. Mã không có phiên này
          được coi là đã ngừng giao dịch / hủy niêm yết nên bị loại.

    Trả về bản sao DataFrame chỉ gồm các mã hợp lệ.
    """

    # Ngày mới nhất của toàn bộ dữ liệu (dùng làm mốc kiểm tra mã còn giao dịch)
    latest_date = df["Date"].max()

    # Thống kê số dòng (số phiên) và ngày giao dịch cuối cùng của từng mã
    stock_info = df.groupby("Ticker").agg(
        n_sessions=("Date", "size"),
        last_date=("Date", "max")
    )

    # Lấy những mã thỏa mãn cả 2 điều kiện
    valid_tickers = stock_info[
        (stock_info["n_sessions"] >= min_sessions)
        & (stock_info["last_date"] == latest_date)
    ].index

    # Chỉ giữ dữ liệu của các mã hợp lệ
    return df[df["Ticker"].isin(valid_tickers)].copy()


# ==================================================
# FEATURE 1: CAGR (Compound Annual Growth Rate)
# ==================================================
# CAGR = (Giá cuối kỳ / Giá đầu kỳ) ^ (1 / Số năm) - 1
# Cho biết trung bình mỗi năm giá cổ phiếu tăng/giảm bao nhiêu % (tính lãi kép).

def annualized_return(df):
    """
    Tính CAGR cho từng mã.

    Yêu cầu df đã sắp xếp theo Ticker, Date để "first"/"last" lấy đúng
    phiên đầu tiên và phiên cuối cùng.

    Trả về DataFrame gồm: Ticker, first_price, last_price, first_date,
    last_date, n_sessions, years, CAGR.
    """

    # Lấy giá và ngày của phiên đầu tiên, phiên cuối cùng, cùng số phiên của từng mã
    result = df.groupby("Ticker").agg(
        first_price=("Close", "first"),
        last_price=("Close", "last"),
        first_date=("Date", "first"),
        last_date=("Date", "last"),
        n_sessions=("Date", "count")
    )

    # Độ dài giai đoạn quan sát tính theo năm:
    # số ngày lịch giữa phiên đầu và phiên cuối chia cho 365.25 (tính cả năm nhuận)
    result["years"] = (
        result["last_date"] - result["first_date"]
    ).dt.days / 365.25

    # Loại các mã không tính được CAGR: ít hơn 2 phiên, giá không dương
    # (tránh chia cho 0 / lũy thừa số âm) hoặc khoảng thời gian bằng 0
    result = result[
        (result["n_sessions"] >= 2)
        & (result["first_price"] > 0)
        & (result["last_price"] > 0)
        & (result["years"] > 0)
    ].copy()

    # Tính CAGR theo công thức lãi kép
    result["CAGR"] = (
        (result["last_price"] / result["first_price"])
        ** (1 / result["years"]) - 1
    )

    return result.reset_index()


# ==================================================
# FEATURE 2: ANNUALIZED VOLATILITY
# ==================================================
# Volatility: độ lệch chuẩn của tỷ suất sinh lời theo ngày, quy đổi về năm.
#   - Volatility cao : tỷ suất sinh lời biến động mạnh, rủi ro biến động giá cao.
#   - Volatility thấp: tỷ suất sinh lời ít biến động, giá ổn định hơn.
# Công thức: Volatility_năm = std(r_ngày) * sqrt(252)

def annualized_volatility(df):
    """
    Tính độ biến động hằng năm cho từng mã.

    Trả về DataFrame gồm: Ticker, Annualized_Volatility.
    """

    # Tạo bản sao để không thêm cột mới vào DataFrame gốc
    df = df.copy()

    # Tỷ suất sinh lời theo phiên: r_t = P_t / P_(t-1) - 1.
    # Tính riêng theo từng mã nên phiên đầu tiên của mỗi mã là NaN (không có phiên trước).
    df["Daily_Return"] = df.groupby("Ticker")["Close"].pct_change()

    # Độ lệch chuẩn mẫu (ddof=1, mặc định của pandas) của tỷ suất sinh lời ngày.
    # Giá trị NaN tự động được bỏ qua.
    result = df.groupby("Ticker")["Daily_Return"].std()

    # Quy đổi về năm: nhân căn bậc hai của 252 phiên giao dịch/năm
    result = result * np.sqrt(252)

    # Đặt tên cột kết quả
    result.name = "Annualized_Volatility"

    return result.reset_index()


# ==================================================
# FEATURE 3: MAXIMUM DRAWDOWN
# ==================================================
# Drawdown tại phiên t = (P_t - Đỉnh_t) / Đỉnh_t, với Đỉnh_t = giá cao nhất từ đầu đến t.
# Max Drawdown = Drawdown nhỏ nhất (âm nhất) => mức lỗ tệ nhất nếu mua ở đỉnh.
# Giá trị nằm trong [-1, 0]; bằng 0 khi giá chưa từng giảm xuống dưới đỉnh trước đó.

def maximum_drawdown(df):
    """
    Tính Maximum Drawdown cho từng mã.

    Trả về DataFrame gồm: Ticker, Max_Drawdown.
    """

    # Tạo bản sao dữ liệu để không thay đổi DataFrame gốc
    data = df.copy()

    # Sắp xếp theo mã và thời gian (cummax cần đúng thứ tự thời gian)
    data = data.sort_values(["Ticker", "Date"])

    # Đỉnh lũy kế: giá đóng cửa cao nhất từ phiên đầu tiên đến phiên hiện tại của mỗi mã
    data["Peak"] = data.groupby("Ticker")["Close"].cummax()

    # Mức sụt giảm so với đỉnh tại từng phiên (luôn <= 0)
    data["Drawdown"] = (data["Close"] - data["Peak"]) / data["Peak"]

    # Lấy giá trị Drawdown nhỏ nhất (sụt giảm sâu nhất) của từng mã
    mdd = (
        data.groupby("Ticker")["Drawdown"]
        .min()
        .reset_index(name="Max_Drawdown")
    )

    return mdd


# ==================================================
# FEATURE 4: SHARPE RATIO
# ==================================================
# Đo lợi nhuận vượt mức lãi suất phi rủi ro trên mỗi đơn vị rủi ro (biến động).
# Sharpe = (252 * mean(r_ngày) - risk_free_rate) / (std(r_ngày) * sqrt(252))
#   - Sharpe > 0: lợi nhuận bình quân cao hơn lãi suất phi rủi ro.
#   - Sharpe = 0: lợi nhuận bình quân năm đúng bằng lãi suất phi rủi ro.
#   - Sharpe < 0: lợi nhuận bình quân thấp hơn lãi suất phi rủi ro.
# Lưu ý: lợi nhuận năm ở đây là trung bình cộng ngày * 252, KHÁC với CAGR (lãi kép).

def sharpe_ratio(df, risk_free_rate=0.04):
    """
    Tính Sharpe Ratio cho từng mã.

    risk_free_rate: lãi suất phi rủi ro theo năm, mặc định giả định 4%/năm.

    Trả về DataFrame gồm: Ticker, Sharpe_Ratio.
    """

    # Tạo bản sao dữ liệu để không thay đổi DataFrame gốc
    data = df.copy()

    # Tỷ suất sinh lời theo phiên của từng mã (phiên đầu tiên mỗi mã là NaN)
    data["Daily_Return"] = data.groupby("Ticker")["Close"].pct_change()

    # Tỷ suất sinh lời trung bình theo ngày của từng mã
    mean_return = data.groupby("Ticker")["Daily_Return"].mean()

    # Độ lệch chuẩn mẫu của tỷ suất sinh lời ngày
    std_return = data.groupby("Ticker")["Daily_Return"].std()

    # Quy đổi lợi nhuận trung bình về năm (252 phiên/năm)
    annual_return = mean_return * 252

    # Quy đổi Volatility về năm (giống hàm annualized_volatility)
    annual_volatility = std_return * np.sqrt(252)

    # Sharpe Ratio = lợi nhuận vượt lãi suất phi rủi ro / độ biến động
    sharpe = (annual_return - risk_free_rate) / annual_volatility

    # Nếu Volatility = 0 thì phép chia cho ra ±inf => đổi thành NaN
    # để bước làm sạch (check_new_csv.py) loại bỏ
    sharpe = sharpe.replace([np.inf, -np.inf], np.nan)

    # Đặt tên cột kết quả
    sharpe.name = "Sharpe_Ratio"

    return sharpe.reset_index()


# ==================================================
# CHẠY TRỰC TIẾP: XEM CHỈ SỐ CỦA MỘT MÃ CỔ PHIẾU
# ==================================================

if __name__ == "__main__":

    # Nhập mã cần xem (bỏ khoảng trắng, đổi sang chữ hoa)
    ticker = input("Nhập mã cổ phiếu: ").strip().upper()

    # Lọc cổ phiếu: đủ 252 phiên và còn giao dịch ở ngày mới nhất
    df = filter_stocks(df, min_sessions=252)

    print(f"Số cổ phiếu đủ điều kiện: {df['Ticker'].nunique()}")

    # 1. Tính CAGR cho toàn bộ cổ phiếu (bảng gốc để ghép các feature khác vào)
    features = annualized_return(df)

    # 2. Tính Volatility cho toàn bộ cổ phiếu
    volatility = annualized_volatility(df)

    # Ghép Volatility vào bảng features theo Ticker
    features = features.merge(volatility, on="Ticker", how="left")

    # 3. Tính Maximum Drawdown cho toàn bộ cổ phiếu
    mdd = maximum_drawdown(df)

    # Ghép Maximum Drawdown vào bảng features theo Ticker
    features = features.merge(mdd, on="Ticker", how="left")

    # 4. Tính Sharpe Ratio cho toàn bộ cổ phiếu
    sharpe = sharpe_ratio(df)

    # Ghép Sharpe Ratio vào bảng features theo Ticker
    features = features.merge(sharpe, on="Ticker", how="left")

    # 5. Lấy dòng dữ liệu của mã người dùng đã nhập
    stock = features[features["Ticker"] == ticker]

    if stock.empty:
        # Mã không tồn tại hoặc đã bị loại ở bước lọc
        print(f"Không tìm thấy mã {ticker}!")
    else:
        s = stock.iloc[0]

        # Giả sử mua 1000 cổ phiếu tại phiên đầu tiên và giữ đến phiên cuối cùng
        quantity = 1000

        # Giá trị khoản đầu tư ban đầu và giá trị cuối kỳ.
        # Vì CAGR được suy ra từ chính giá đầu/cuối kỳ nên final_value
        # bằng quantity * last_price (chưa tính cổ tức, phí, thuế).
        initial_value = quantity * s["first_price"]
        final_value = initial_value * (1 + s["CAGR"]) ** s["years"]

        print(f"\n========== {ticker} ==========")
        print(f"Ngày mua: {s['first_date']:%d/%m/%Y}")
        print(f"Giá mua (Close): {s['first_price']:,.2f}")

        print(f"Ngày cuối cùng: {s['last_date']:%d/%m/%Y}")
        print(f"Giá cuối kỳ (Close): {s['last_price']:,.2f}")

        print(f"Thời gian nắm giữ: {s['years']:.2f} năm")

        # Hiển thị 4 đặc trưng
        print(f"CAGR: {s['CAGR']:.2%}")
        print(f"Annualized Volatility: {s['Annualized_Volatility']:.2%}")
        print(f"Maximum Drawdown: {s['Max_Drawdown']:.2%}")
        print(f"Sharpe Ratio: {s['Sharpe_Ratio']:.2f}")

        # Hiển thị kết quả giả định khi đầu tư 1000 cổ phiếu
        print(f"\nGiá trị ban đầu (1000 CP): {initial_value:,.2f}")
        print(f"Giá trị hiện tại (1000 CP): {final_value:,.2f}")
        print(f"Lãi/Lỗ: {final_value - initial_value:+,.2f}")
