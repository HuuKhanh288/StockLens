import pandas as pd

# Đọc dữ liệu
df = pd.read_csv("data/stock_cleaned.csv")

# Hàm đếm số cổ phiếu
def count_stocks(df):
    return df["Ticker"].nunique()

# Thống kê
total_stocks = count_stocks(df)
total_rows = len(df)

print(f"Tổng số cổ phiếu: {total_stocks}")
print(f"Tổng số dòng dữ liệu: {total_rows}")