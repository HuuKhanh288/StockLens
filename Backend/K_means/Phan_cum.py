"""
Phan_cum.py - Bước 5 của quy trình K-Means: phân cụm cổ phiếu thành 4 nhóm.

Đầu vào : stock_features_no_outliers_scaled.csv (do standardization.py tạo ra)
Đầu ra  : stock_clusters.csv - Ticker, 4 đặc trưng đã chuẩn hóa và nhãn Cluster (0-3)

Tâm cụm ban đầu được chọn cố định từ 4 mã cổ phiếu (initial_tickers) thay vì
khởi tạo ngẫu nhiên, nên mỗi lần chạy trên cùng dữ liệu đều cho cùng kết quả.
"""
import pandas as pd
from pathlib import Path
from sklearn.cluster import KMeans

BASE_DIR = Path(__file__).resolve().parent

# Đọc dữ liệu đã chuẩn hóa Z-score
df = pd.read_csv(BASE_DIR / "stock_features_no_outliers_scaled.csv")

# 4 đặc trưng dùng để phân cụm
features = [
    "CAGR",
    "Annualized_Volatility",
    "Max_Drawdown",
    "Sharpe_Ratio"
]

# Chọn 4 cổ phiếu làm tâm khởi tạo.
# Thứ tự trong danh sách quyết định số hiệu cụm: tâm khởi tạo từ ABR là cụm 0,
# ABI là cụm 1, VOS là cụm 2, KOS là cụm 3. Tên cụm trong visualization.py
# dựa vào thứ tự này. Cả 4 mã phải còn trong dữ liệu sau tiền xử lý,
# nếu không .loc bên dưới sẽ báo KeyError.
initial_tickers = ["ABR", "ABI", "VOS", "KOS"]

# Lấy vectơ 4 đặc trưng (đã chuẩn hóa) của các mã trên, dạng mảng 4 x 4
initial_centers = (
    df.set_index("Ticker")
      .loc[initial_tickers, features]
      .to_numpy()
)

# Khởi tạo K-Means:
#   - n_clusters=4         : chia thành 4 cụm
#   - init=initial_centers : dùng tâm khởi tạo cố định ở trên
#   - n_init=1             : chỉ chạy 1 lần vì tâm khởi tạo đã cố định
#                            (chạy nhiều lần cũng cho cùng kết quả)
kmeans = KMeans(
    n_clusters=4,
    init=initial_centers,
    n_init=1
)

# Huấn luyện mô hình và gán nhãn cụm (0-3) cho từng cổ phiếu
df["Cluster"] = kmeans.fit_predict(df[features])

# In danh sách cổ phiếu trong từng cụm
for cluster in sorted(df["Cluster"].unique()):

    print(f"\n===== CLUSTER {cluster} =====")

    stocks = df[df["Cluster"] == cluster]

    print(stocks[["Ticker", "Cluster"]].to_string(index=False))

    print("Số lượng cổ phiếu:", len(stocks))

# Xuất kết quả (đặc trưng vẫn ở thang đo đã chuẩn hóa)
df.to_csv(BASE_DIR / "stock_clusters.csv", index=False)

# In số lượng cổ phiếu của từng cụm, sắp xếp theo số hiệu cụm
print(df["Cluster"].value_counts().sort_index())
