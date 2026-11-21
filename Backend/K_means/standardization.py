"""
standardization.py - Bước 4 của quy trình K-Means: chuẩn hóa Z-score 4 đặc trưng.

Đầu vào : stock_features_no_outliers.csv (do remove_outliers.py tạo ra)
Đầu ra  : stock_features_no_outliers_scaled.csv

Công thức: z = (x - mean) / std, tính riêng cho từng đặc trưng.
Sau khi chuẩn hóa, mỗi đặc trưng có trung bình 0 và độ lệch chuẩn 1.

Lý do cần chuẩn hóa: K-Means dùng khoảng cách Euclid. Nếu không chuẩn hóa,
đặc trưng có thang đo lớn hơn (ví dụ Sharpe so với Max_Drawdown) sẽ chi phối
khoảng cách và kết quả phân cụm.
"""
import pandas as pd
from sklearn.preprocessing import StandardScaler
from pathlib import Path

# 1. Đường dẫn dữ liệu
BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "stock_features_no_outliers.csv"
OUTPUT_FILE = BASE_DIR / "stock_features_no_outliers_scaled.csv"

# 2. Đọc dữ liệu đã làm sạch và loại ngoại lai
df = pd.read_csv(INPUT_FILE)

# 3. Danh sách các đặc trưng cần chuẩn hóa
features = [
    "CAGR",
    "Annualized_Volatility",
    "Max_Drawdown",
    "Sharpe_Ratio"
]

# 4. Khởi tạo bộ chuẩn hóa Z-score
scaler = StandardScaler()

# 5. Học mean/std từ dữ liệu (fit) rồi chuẩn hóa (transform) 4 đặc trưng.
#    Kết quả là mảng NumPy, không còn tên cột và cột Ticker.
scaled_data = scaler.fit_transform(df[features])

# 6. Đưa mảng kết quả về DataFrame, giữ nguyên index để ghép lại đúng mã cổ phiếu
df_scaled = pd.DataFrame(
    scaled_data,
    columns=features,
    index=df.index
)

# 7. Thêm lại cột Ticker vào vị trí đầu tiên để nhận diện từng mã
df_scaled.insert(0, "Ticker", df["Ticker"])

# 8. Kiểm tra dữ liệu sau chuẩn hóa
print("===== DỮ LIỆU SAU CHUẨN HÓA =====")
print(df_scaled.head(10))

# Trung bình của mỗi đặc trưng phải xấp xỉ 0
print("\n===== GIÁ TRỊ TRUNG BÌNH =====")
print(df_scaled[features].mean())

# Độ lệch chuẩn phải bằng 1. Dùng ddof=0 (độ lệch chuẩn tổng thể)
# vì StandardScaler cũng chia cho độ lệch chuẩn tổng thể.
print("\n===== ĐỘ LỆCH CHUẨN =====")
print(df_scaled[features].std(ddof=0))

# 9. Xuất file CSV
df_scaled.to_csv(OUTPUT_FILE, index=False)

print("\nĐã xuất file:", OUTPUT_FILE)
