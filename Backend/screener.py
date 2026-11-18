import pandas as pd
from pathlib import Path

from indicators import (
    calculate_sma,
    calculate_kijun,
    calculate_rsi,
    calculate_ichimoku
)


# ==================================================
# 1. ĐƯỜNG DẪN DỮ LIỆU
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "stock_cleaned.csv"


# ==================================================
# 2. PHÁT HIỆN ĐÁY GIÁ (SWING LOW)
# ==================================================

def find_swing_lows(series, window=3):

    lows = []

    for i in range(window, len(series) - window):

        current = series.iloc[i]

        left = series.iloc[i-window:i]
        right = series.iloc[i+1:i+window+1]

        if current < left.min() and current < right.min():
            lows.append(i)

    return lows


# ==================================================
# 3. PHÁT HIỆN PHÂN KỲ DƯƠNG RSI
# ==================================================

def detect_bullish_divergence(
    df,
    lookback=60,
    window=3,
    max_age=10
):

    if len(df) < 30:
        return False

    stock = df.tail(lookback).reset_index(drop=True)

    swing_lows = find_swing_lows(
        stock["Low"],
        window
    )

    if len(swing_lows) < 2:
        return False

    for i in range(len(swing_lows) - 1, 0, -1):

        idx1 = swing_lows[i - 1]
        idx2 = swing_lows[i]

        price1 = stock["Low"].iloc[idx1]
        price2 = stock["Low"].iloc[idx2]

        rsi1 = stock["RSI14"].iloc[idx1]
        rsi2 = stock["RSI14"].iloc[idx2]

        if pd.isna(rsi1) or pd.isna(rsi2):
            continue

        # Phân kỳ phải xuất hiện gần đây
        if len(stock) - 1 - idx2 > max_age:
            break

        # Giá tạo đáy thấp hơn, RSI tạo đáy cao hơn
        if price2 < price1 and rsi2 > rsi1:
            return True

    return False


# ==================================================
# 4. TÍNH CHỈ BÁO CHO TỪNG CỔ PHIẾU
# ==================================================

def add_indicators(stock):

    stock = stock.sort_values("Date").copy()

    # MA200
    stock["MA200"] = calculate_sma(stock, 200)

    # Kijun
    stock["Kijun69"] = calculate_kijun(stock, 69)
    stock["Kijun129"] = calculate_kijun(stock, 129)
    stock["Kijun234"] = calculate_kijun(stock, 234)

    # RSI14
    stock["RSI14"] = calculate_rsi(stock, 14)

    # Mây Ichimoku
    span_a, span_b = calculate_ichimoku(stock)

    stock["Span_A"] = span_a
    stock["Span_B"] = span_b

    return stock


# ==================================================
# 5. LOGIC KIỂM TRA 6 TIÊU CHÍ
# ==================================================

def check_conditions(stock):

    latest = stock.iloc[-1]
    close = latest["Close"]

    conditions = {

        # 1. Giá nằm trên Kijun69
        "kijun69": (
            pd.notna(latest["Kijun69"])
            and close > latest["Kijun69"]
        ),

        # 2. Giá nằm trên Kijun129
        "kijun129": (
            pd.notna(latest["Kijun129"])
            and close > latest["Kijun129"]
        ),

        # 3. Giá nằm trên Kijun234
        "kijun234": (
            pd.notna(latest["Kijun234"])
            and close > latest["Kijun234"]
        ),

        # 4. Giá nằm trên MA200
        "ma200": (
            pd.notna(latest["MA200"])
            and close > latest["MA200"]
        ),

        # 5. Giá nằm trên mây Ichimoku
        "ichimoku_cloud": (
            pd.notna(latest["Span_A"])
            and pd.notna(latest["Span_B"])
            and close > latest["Span_A"]
            and close > latest["Span_B"]
        ),

        # 6. Xuất hiện phân kỳ dương RSI
        "rsi_divergence": detect_bullish_divergence(stock)

    }

    return conditions


# ==================================================
# 6. THUẬT TOÁN LỌC TOÀN BỘ CỔ PHIẾU
# ==================================================

def screen_stocks(df, selected_filters):

    valid_filters = {
        "kijun69",
        "kijun129",
        "kijun234",
        "ma200",
        "ichimoku_cloud",
        "rsi_divergence"
    }

    invalid = set(selected_filters) - valid_filters

    if invalid:
        raise ValueError(f"Tiêu chí không hợp lệ: {invalid}")

    results = []

    # Lọc lần lượt từng cổ phiếu
    for ticker, stock in df.groupby("Ticker"):

        stock = add_indicators(stock)

        # Kiểm tra 6 điều kiện
        conditions = check_conditions(stock)

        # Chỉ xét những tiêu chí người dùng đã chọn
        # Tất cả tiêu chí được chọn phải đúng
        if all(conditions[f] for f in selected_filters):

            latest = stock.iloc[-1]

            results.append({

                "Ticker": ticker,
                "Date": latest["Date"],
                "Close": latest["Close"],

                "MA200": latest["MA200"],

                "Kijun69": latest["Kijun69"],
                "Kijun129": latest["Kijun129"],
                "Kijun234": latest["Kijun234"],

                "RSI14": latest["RSI14"],

                "Span_A": latest["Span_A"],
                "Span_B": latest["Span_B"]

            })

    return pd.DataFrame(results)


# ==================================================
# 7. LỰA CHỌN TIÊU CHÍ LỌC
# ==================================================

def choose_filters():

    filter_options = {

        "1": ("kijun69", "Giá trên dao găm 69"),

        "2": ("kijun129", "Giá trên dao găm 129"),

        "3": ("kijun234", "Giá trên dao găm 234"),

        "4": ("ma200", "Giá trên MA200"),

        "5": ("ichimoku_cloud", "Giá trên mây Ichimoku"),

        "6": ("rsi_divergence", "Phân kỳ dương RSI")

    }

    print("\n========== STOCKLENS ==========\n")

    print("CHỌN CÁC TIÊU CHÍ LỌC CỔ PHIẾU:\n")

    for number, (_, description) in filter_options.items():
        print(f"{number}. {description}")

    print("\nCó thể lựa chọn một hoặc nhiều tiêu chí.")
    print("Ví dụ: 1,3,5")

    while True:

        choice = input("\nNhập tiêu chí muốn lọc: ")

        selected_numbers = [
            number.strip()
            for number in choice.split(",")
        ]

        # Kiểm tra lựa chọn
        if (
            not selected_numbers
            or any(
                number not in filter_options
                for number in selected_numbers
            )
        ):
            print("Lựa chọn không hợp lệ! Vui lòng nhập lại.")
            continue

        # Loại bỏ lựa chọn trùng lặp
        selected_numbers = list(dict.fromkeys(selected_numbers))

        # Chuyển số thành tên tiêu chí
        selected_filters = [
            filter_options[number][0]
            for number in selected_numbers
        ]

        print("\nCÁC TIÊU CHÍ ĐÃ CHỌN:\n")

        for number in selected_numbers:
            print(f"- {filter_options[number][1]}")

        return selected_filters


# ==================================================
# 8. CHẠY CHƯƠNG TRÌNH
# ==================================================

if __name__ == "__main__":

    # Bước 1: Người dùng lựa chọn tiêu chí
    selected_filters = choose_filters()

    # Bước 2: Đọc dữ liệu
    df = pd.read_csv(DATA_PATH)

    print("\nĐang thực hiện lọc cổ phiếu...\n")

    # Bước 3: Gọi thuật toán lọc
    result = screen_stocks(df, selected_filters)

    # Bước 4: Hiển thị kết quả
    print("\n========== KẾT QUẢ LỌC ==========\n")

    if result.empty:
        print("Không tìm thấy cổ phiếu phù hợp.")

    else:
        print(result.to_string(index=False))

    print(f"\nTổng số cổ phiếu thỏa mãn: {len(result)}")