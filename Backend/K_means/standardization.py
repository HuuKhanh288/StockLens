import pandas as pd
from sklearn.preprocessing import StandardScaler
from pathlib import Path

# 1. Đường dẫn dữ liệu
BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "stock_features_no_outliers.csv"
OUTPUT_FILE = BASE_DIR / "stock_features_no_outliers_scaled.csv"

# 2. Đọc dữ liệu đã làm sạch
df = pd.read_csv(INPUT_FILE)

# 3. Danh sách các đặc trưng cần chuẩn hóa
features = [
    "CAGR",
    "Annualized_Volatility",
    "Max_Drawdown",
    "Sharpe_Ratio"
]

# 4. Khởi tạo bộ chuẩn hóa
scaler = StandardScaler()

# 5. Chuẩn hóa 4 đặc trưng
scaled_data = scaler.fit_transform(df[features])

# 6. Tạo DataFrame mới
df_scaled = pd.DataFrame(
    scaled_data,
    columns=features,
    index=df.index
)

# 7. Thêm lại mã cổ phiếu
df_scaled.insert(0, "Ticker", df["Ticker"])

# 8. Kiểm tra dữ liệu sau chuẩn hóa
print("===== DỮ LIỆU SAU CHUẨN HÓA =====")
print(df_scaled.head(10))

print("\n===== GIÁ TRỊ TRUNG BÌNH =====")
print(df_scaled[features].mean())

print("\n===== ĐỘ LỆCH CHUẨN =====")
print(df_scaled[features].std(ddof=0))

# 9. Xuất file CSV
df_scaled.to_csv(OUTPUT_FILE, index=False)

print("\nĐã xuất file:", OUTPUT_FILE)