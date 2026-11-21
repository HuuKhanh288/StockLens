"""
check_new_csv.py - Bước 2 của quy trình K-Means: kiểm tra và làm sạch file đặc trưng.

Đầu vào : stock_features.csv (cùng thư mục, do new_csv.py tạo ra)
Đầu ra  : stock_features_cleaned.csv

Các dòng bị loại:
    - Thiếu Ticker hoặc thiếu một trong 4 đặc trưng (kể cả giá trị vô hạn).
    - Mã cổ phiếu bị trùng (giữ lại dòng xuất hiện đầu tiên).
    - Giá trị ngoài phạm vi hợp lệ: CAGR < -1, Volatility < 0, Max_Drawdown ngoài [-1, 0].
    - Có BẤT KỲ đặc trưng nào bằng 0 (xem giải thích ở mục 2).
"""
import pandas as pd
import numpy as np
from pathlib import Path

# 1. Đường dẫn và đọc dữ liệu
BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "stock_features.csv"
OUTPUT_FILE = BASE_DIR / "stock_features_cleaned.csv"

df = pd.read_csv(INPUT_FILE)

# Danh sách 4 đặc trưng cần kiểm tra
features = [
    "CAGR",
    "Annualized_Volatility",
    "Max_Drawdown",
    "Sharpe_Ratio"
]

# 2. Kiểm tra thông tin dữ liệu
# Ý nghĩa khi một đặc trưng bằng 0:
#   - CAGR = 0         : giá cuối kỳ bằng đúng giá đầu kỳ.
#   - Volatility = 0   : giá đóng cửa không đổi suốt giai đoạn (mã gần như không
#                        có giao dịch). Khi đó Sharpe không xác định (chia cho 0).
#   - Max_Drawdown = 0 : giá chưa từng giảm xuống dưới đỉnh trước đó. Trường hợp này
#                        CÓ THỂ xảy ra nhưng rất hiếm và thường là dữ liệu bất thường.
#   - Sharpe = 0       : lợi nhuận bình quân năm đúng bằng lãi suất phi rủi ro (4%).
#                        (Không liên quan đến việc độ biến động bằng bao nhiêu.)
# Mục 10 loại TẤT CẢ các dòng có bất kỳ đặc trưng nào bằng 0 để tránh các mã có
# dữ liệu bất thường (giá đứng yên, không giao dịch) làm lệch kết quả phân cụm.
print("===== THÔNG TIN DỮ LIỆU =====")
print("Số lượng cổ phiếu ban đầu:", len(df))  # Mỗi dòng là một mã cổ phiếu
print("Số lượng cột:", len(df.columns))

# 3. Kiểm tra kiểu dữ liệu
print("\n===== KIỂU DỮ LIỆU =====")
print(df.dtypes)

# Chuyển các đặc trưng sang kiểu số; giá trị không chuyển được sẽ thành NaN
for feature in features:
    df[feature] = pd.to_numeric(df[feature], errors="coerce")

# 4. Đếm số giá trị thiếu (NaN) của từng cột
print("\n===== GIÁ TRỊ THIẾU =====")
print(df.isnull().sum())

# 5. Đếm số giá trị vô hạn (inf, -inf) của từng đặc trưng
print("\n===== GIÁ TRỊ VÔ HẠN =====")
print(np.isinf(df[features]).sum())

# 6. Kiểm tra mã cổ phiếu trùng
print("\n===== MÃ CỔ PHIẾU TRÙNG =====")

# keep=False: đánh dấu tất cả các dòng bị trùng (không bỏ qua lần xuất hiện đầu)
duplicate = df[df["Ticker"].duplicated(keep=False)]

print(duplicate.to_string(index=False))

# 7. Thống kê mô tả (count, mean, std, min, quartile, max)
print("\n===== THỐNG KÊ ĐẶC TRƯNG =====")
print(df[features].describe())

# 8. Kiểm tra giá trị ngoài phạm vi hợp lệ
#    - CAGR >= -1        : giá không thể giảm quá 100%
#    - Volatility >= 0   : độ lệch chuẩn không thể âm
#    - -1 <= MDD <= 0    : Drawdown luôn nằm trong khoảng này
#    (Sharpe có thể nhận mọi giá trị thực nên không kiểm tra phạm vi.)
print("\n===== GIÁ TRỊ KHÔNG HỢP LỆ =====")

invalid = (
    (df["CAGR"] < -1) |
    (df["Annualized_Volatility"] < 0) |
    (df["Max_Drawdown"] < -1) |
    (df["Max_Drawdown"] > 0)
)

print(df[invalid].to_string(index=False))

# 9. Liệt kê các mã có đặc trưng bằng 0 (chỉ in ra để xem, việc loại bỏ ở mục 10)
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

# Chuyển giá trị vô hạn thành NaN để dropna bên dưới loại luôn
df = df.replace([np.inf, -np.inf], np.nan)

# Xóa dòng thiếu Ticker hoặc thiếu bất kỳ đặc trưng nào
df = df.dropna(subset=["Ticker"] + features)

# Xóa mã cổ phiếu trùng, giữ lại dòng xuất hiện đầu tiên
df = df.drop_duplicates(subset=["Ticker"])

# Chỉ giữ các dòng có giá trị nằm trong phạm vi hợp lệ (ngược với điều kiện ở mục 8)
df = df[
    (df["CAGR"] >= -1) &
    (df["Annualized_Volatility"] >= 0) &
    (df["Max_Drawdown"] >= -1) &
    (df["Max_Drawdown"] <= 0)
]

# Xóa toàn bộ dòng nếu bất kỳ đặc trưng nào bằng 0 (lý do: xem mục 2)
df = df[(df[features] != 0).all(axis=1)]

# 11. Xuất file dữ liệu đã làm sạch
df.to_csv(OUTPUT_FILE, index=False)

# 12. In kết quả
print("Số cổ phiếu ban đầu:", original_count)
print("Số cổ phiếu sau khi làm sạch:", len(df))
print("Số cổ phiếu bị loại:", original_count - len(df))

print("\nĐã xuất file:", OUTPUT_FILE)
