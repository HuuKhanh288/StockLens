import pandas as pd
from pathlib import Path

# 1. Đường dẫn dữ liệu
BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "stock_features_cleaned.csv"
OUTPUT_FILE = BASE_DIR / "stock_features_no_outliers.csv"
REMOVED_FILE = BASE_DIR / "stock_outliers_removed.csv"

# 2. Đọc dữ liệu
df = pd.read_csv(INPUT_FILE)

features = [
    "CAGR",
    "Annualized_Volatility",
    "Max_Drawdown",
    "Sharpe_Ratio"
]

print("===== KIỂM TRA NGOẠI LAI =====")
print("Số cổ phiếu ban đầu:", len(df))

# 3. Khởi tạo bộ đánh dấu ngoại lai
outlier_mask = pd.Series(False, index=df.index)

# 4. Kiểm tra ngoại lai từng đặc trưng
for feature in features:

    # Tính các phân vị
    Q1 = df[feature].quantile(0.25)
    Q3 = df[feature].quantile(0.75)

    # Khoảng tứ phân vị
    IQR = Q3 - Q1

    # Xác định ngưỡng ngoại lai
    lower = Q1 - 3 * IQR
    upper = Q3 + 3 * IQR

    # Kiểm tra giá trị ngoài ngưỡng
    mask = (df[feature] < lower) | (df[feature] > upper)

    print(f"\n===== {feature} =====")
    print("Q1:", round(Q1, 4))
    print("Q3:", round(Q3, 4))
    print("IQR:", round(IQR, 4))
    print("Ngưỡng dưới:", round(lower, 4))
    print("Ngưỡng trên:", round(upper, 4))

    print("Số cổ phiếu ngoại lai:", mask.sum())

    # In những cổ phiếu ngoại lai
    if mask.any():
        print(df.loc[mask, ["Ticker", feature]].to_string(index=False))
    else:
        print("Không có ngoại lai")

    # Đánh dấu các dòng có ít nhất một đặc trưng ngoại lai
    outlier_mask = outlier_mask | mask


# 5. Phân chia dữ liệu
df_removed = df[outlier_mask].copy()

df_clean = df[~outlier_mask].copy()


# 6. Xuất dữ liệu
df_clean.to_csv(OUTPUT_FILE, index=False)

df_removed.to_csv(REMOVED_FILE, index=False)


# 7. In kết quả
print("\n===== KẾT QUẢ LOẠI BỎ NGOẠI LAI =====")

print("Số cổ phiếu ban đầu:", len(df))
print("Số cổ phiếu bị loại:", len(df_removed))
print("Số cổ phiếu còn lại:", len(df_clean))

print("\nDanh sách cổ phiếu bị loại:")

if not df_removed.empty:
    print(df_removed.to_string(index=False))
else:
    print("Không có cổ phiếu bị loại")

print("\nĐã xuất file:")
print(OUTPUT_FILE)
print(REMOVED_FILE)