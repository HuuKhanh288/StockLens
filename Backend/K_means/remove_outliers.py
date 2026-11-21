"""
remove_outliers.py - Bước 3 của quy trình K-Means: loại bỏ cổ phiếu ngoại lai bằng IQR.

Đầu vào : stock_features_cleaned.csv (do check_new_csv.py tạo ra)
Đầu ra  : stock_features_no_outliers.csv  - các mã được giữ lại
          stock_outliers_removed.csv      - các mã bị loại (để đối chiếu)

Phương pháp: với mỗi đặc trưng, tính Q1, Q3 và IQR = Q3 - Q1.
Giá trị nằm ngoài [Q1 - 3*IQR, Q3 + 3*IQR] là ngoại lai. Hệ số 3 (thay vì 1.5
thông dụng) chỉ loại các ngoại lai cực đoan, tránh loại quá nhiều cổ phiếu.
Một mã bị loại nếu có ÍT NHẤT MỘT đặc trưng là ngoại lai.

K-Means dùng khoảng cách Euclid và trung bình cụm nên rất nhạy với ngoại lai,
vì vậy bước này cần chạy trước khi chuẩn hóa và phân cụm.
"""
import pandas as pd
from pathlib import Path

# 1. Đường dẫn dữ liệu
BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "stock_features_cleaned.csv"
OUTPUT_FILE = BASE_DIR / "stock_features_no_outliers.csv"
REMOVED_FILE = BASE_DIR / "stock_outliers_removed.csv"

# 2. Đọc dữ liệu
df = pd.read_csv(INPUT_FILE)

# Danh sách 4 đặc trưng cần kiểm tra ngoại lai
features = [
    "CAGR",
    "Annualized_Volatility",
    "Max_Drawdown",
    "Sharpe_Ratio"
]

print("===== KIỂM TRA NGOẠI LAI =====")
print("Số cổ phiếu ban đầu:", len(df))

# 3. Khởi tạo mặt nạ ngoại lai: ban đầu chưa có mã nào bị đánh dấu (toàn False)
outlier_mask = pd.Series(False, index=df.index)

# 4. Kiểm tra ngoại lai từng đặc trưng.
#    Ngưỡng của mọi đặc trưng đều tính trên cùng tập dữ liệu ban đầu
#    (không tính lại sau khi loại từng đặc trưng).
for feature in features:

    # Phân vị thứ 25% (Q1) và 75% (Q3)
    Q1 = df[feature].quantile(0.25)
    Q3 = df[feature].quantile(0.75)

    # Khoảng tứ phân vị
    IQR = Q3 - Q1

    # Ngưỡng ngoại lai cực đoan (hệ số 3)
    lower = Q1 - 3 * IQR
    upper = Q3 + 3 * IQR

    # True với các mã có giá trị nằm ngoài ngưỡng
    mask = (df[feature] < lower) | (df[feature] > upper)

    print(f"\n===== {feature} =====")
    print("Q1:", round(Q1, 4))
    print("Q3:", round(Q3, 4))
    print("IQR:", round(IQR, 4))
    print("Ngưỡng dưới:", round(lower, 4))
    print("Ngưỡng trên:", round(upper, 4))

    print("Số cổ phiếu ngoại lai:", mask.sum())

    # In những cổ phiếu ngoại lai của đặc trưng này
    if mask.any():
        print(df.loc[mask, ["Ticker", feature]].to_string(index=False))
    else:
        print("Không có ngoại lai")

    # Gộp bằng phép OR: mã có ít nhất một đặc trưng ngoại lai sẽ bị đánh dấu
    outlier_mask = outlier_mask | mask


# 5. Tách dữ liệu thành 2 phần: bị loại và được giữ lại
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
