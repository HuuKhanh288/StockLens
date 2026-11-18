import pandas as pd


# ==================================================
# 1. SIMPLE MOVING AVERAGE (SMA)
# ==================================================

def calculate_sma(df, period):

    sma = df["Close"].rolling(
        window=period,
        min_periods=period
    ).mean()

    return sma


# ==================================================
# 2. KIJUN-SEN
# ==================================================

def calculate_kijun(df, period):

    highest = df["High"].rolling(
        window=period,
        min_periods=period
    ).max()

    lowest = df["Low"].rolling(
        window=period,
        min_periods=period
    ).min()

    kijun = (highest + lowest) / 2

    return kijun


# ==================================================
# 3. RSI - WILDER
# ==================================================

def calculate_rsi(df, period=14):

    close = df["Close"].astype(float)

    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = pd.Series(float("nan"), index=df.index)
    avg_loss = pd.Series(float("nan"), index=df.index)

    if len(df) <= period:
        return avg_gain

    initial_gain = gain.iloc[1:period + 1].mean()
    initial_loss = loss.iloc[1:period + 1].mean()

    avg_gain.iloc[period] = initial_gain
    avg_loss.iloc[period] = initial_loss

    for i in range(period + 1, len(df)):

        avg_gain.iloc[i] = (
            avg_gain.iloc[i - 1] * (period - 1)
            + gain.iloc[i]
        ) / period

        avg_loss.iloc[i] = (
            avg_loss.iloc[i - 1] * (period - 1)
            + loss.iloc[i]
        ) / period

    rs = avg_gain / avg_loss.replace(0, float("nan"))

    rsi = 100 - (100 / (1 + rs))

    # Không có phiên giảm, nhưng có phiên tăng
    rsi = rsi.mask(
        (avg_loss == 0) & (avg_gain > 0),
        100
    )

    # Không có cả tăng lẫn giảm
    rsi = rsi.mask(
        (avg_loss == 0) & (avg_gain == 0),
        50
    )

    return rsi


# ==================================================
# 4. ICHIMOKU
# Bộ thông số: 9 - 17 - 26 - 26 - 26
# ==================================================

def calculate_ichimoku(df):

    # Tính Tenkan 9 và Kijun 17
    tenkan = calculate_kijun(df, 9)
    kijun = calculate_kijun(df, 17)

    # Tính hai đường tạo mây
    span_a = (tenkan + kijun) / 2
    span_b = calculate_kijun(df, 26)

    # Đưa mây về đúng vị trí thời gian trên biểu đồ
    span_a = span_a.shift(26)
    span_b = span_b.shift(26)

    return span_a, span_b