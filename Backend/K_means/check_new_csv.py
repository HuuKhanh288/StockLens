import pandas as pd
import numpy as np
from pathlib import Path

# 1. Đọc dữ liệu
BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "stock_features.csv"
OUTPUT_FILE = BASE_DIR / "stock_features_cleaned.csv"

df = pd.read_csv(INPUT_FILE)

features = [
    "CAGR",
    "Annualized_Volatility",
    "Max_Drawdown",
    "Sharpe_Ratio"
]

# 2. Kiểm tra thông tin dữ liệu
# CAGR NÀY CÓ THỂ = 0 (GIÁ TRỊ ĐẦU KỲ CÓ THỂ BẰNG GIÁ TRỊ CUỐI KỲ)
# VOLITALITY KHÔNG THỂ = 0 VÌ 1 CỔ PHIẾU NẾU KO BIẾN ĐỘNG THÌ KO ĐC 
# MAX_DRAWDOWN KHÔNG THỂ = 0 VÌ 1 CỔ PHIẾU KO THỂ KO ĐIỀU CHỈNH MÀ TĂNG 1 MẠCH. KIỂU J CX CÓ ĐIỀU CHỈNH
# SHARPE CÓ THỂ BẰNG 0 VÌ ĐỘ BIẾN ĐỘNG CÓ THỂ = TỶ LỆ RỦI RO
print("===== THÔNG TIN DỮ LIỆU =====")
print("Số lượng cổ phiếu ban đầu:", len(df))
print("Số lượng cột:", len(df.columns))

# 3. Kiểm tra kiểu dữ liệu
print("\n===== KIỂU DỮ LIỆU =====")
print(df.dtypes)

# Chuyển các đặc trưng sang kiểu số
for feature in features:
    df[feature] = pd.to_numeric(df[feature], errors="coerce")

# 4. Kiểm tra giá trị thiếu
print("\n===== GIÁ TRỊ THIẾU =====")
print(df.isnull().sum())

# 5. Kiểm tra giá trị vô hạn
print("\n===== GIÁ TRỊ VÔ HẠN =====")
print(np.isinf(df[features]).sum())

# 6. Kiểm tra mã cổ phiếu trùng
print("\n===== MÃ CỔ PHIẾU TRÙNG =====")

duplicate = df[df["Ticker"].duplicated(keep=False)]

print(duplicate.to_string(index=False))

# 7. Thống kê mô tả
print("\n===== THỐNG KÊ ĐẶC TRƯNG =====")
print(df[features].describe())

# 8. Kiểm tra giá trị ngoài phạm vi hợp lệ
print("\n===== GIÁ TRỊ KHÔNG HỢP LỆ =====")

invalid = (
    (df["CAGR"] < -1) |
    (df["Annualized_Volatility"] < 0) |
    (df["Max_Drawdown"] < -1) |
    (df["Max_Drawdown"] > 0)
)

print(df[invalid].to_string(index=False))

# 9. Kiểm tra các giá trị bằng 0
print("\n===== CỔ PHIẾU CÓ GIÁ TRỊ BẰNG 0 =====")

for feature in features:

    stocks_zero = df[df[feature] == 0]

    print(f"\n{feature} = 0")
    print("Số lượng:", len(stocks_zero))

    if not stocks_zero.empty:
        print(stocks_zero[["Ticker", feature]].to_string(index=False))
    else:
        print("Không có")

# 10. Lọc dữ liệu
print("\n===== LÀM SẠCH DỮ LIỆU =====")

original_count = len(df)

# Chuyển giá trị vô hạn thành NaN
df = df.replace([np.inf, -np.inf], np.nan)

# Xóa dòng có dữ liệu thiếu
df = df.dropna(subset=["Ticker"] + features)

# Xóa các mã cổ phiếu trùng
df = df.drop_duplicates(subset=["Ticker"])

# Xóa các dòng có giá trị không hợp lệ
df = df[
    (df["CAGR"] >= -1) &
    (df["Annualized_Volatility"] >= 0) &
    (df["Max_Drawdown"] >= -1) &
    (df["Max_Drawdown"] <= 0)
]

# Xóa toàn bộ dòng nếu bất kỳ đặc trưng nào bằng 0
df = df[(df[features] != 0).all(axis=1)]

# 11. Xuất file dữ liệu mới
df.to_csv(OUTPUT_FILE, index=False)

# 12. In kết quả
print("Số cổ phiếu ban đầu:", original_count)
print("Số cổ phiếu sau khi làm sạch:", len(df))
print("Số cổ phiếu bị loại:", original_count - len(df))

print("\nĐã xuất file:", OUTPUT_FILE)