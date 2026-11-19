# PHÂN CỤM CỔ PHIẾU LẤY DỮ LIỆU TỪ FILE stock_feature_no_outliers_scaled.csv => stock_clusters.csv
import pandas as pd
from pathlib import Path
from sklearn.cluster import KMeans

BASE_DIR = Path(__file__).resolve().parent

df = pd.read_csv(BASE_DIR / "stock_features_no_outliers_scaled.csv")

features = [
    "CAGR",
    "Annualized_Volatility",
    "Max_Drawdown",
    "Sharpe_Ratio"
]

# Chọn 4 cổ phiếu làm tâm khởi tạo
initial_tickers = ["ABR", "ABI", "VOS", "KOS"]

# Lấy 4 đặc trưng của các cổ phiếu đã chọn
initial_centers = (
    df.set_index("Ticker")
      .loc[initial_tickers, features]
      .to_numpy()
)

# Khởi tạo K-Means
kmeans = KMeans(
    n_clusters=4,
    init=initial_centers,
    n_init=1
)

# Phân cụm
df["Cluster"] = kmeans.fit_predict(df[features])

# In danh sách cổ phiếu trong từng cụm
for cluster in sorted(df["Cluster"].unique()):

    print(f"\n===== CLUSTER {cluster} =====")

    stocks = df[df["Cluster"] == cluster]

    print(stocks[["Ticker", "Cluster"]].to_string(index=False))

    print("Số lượng cổ phiếu:", len(stocks))

# Xuất kết quả
df.to_csv(BASE_DIR / "stock_clusters.csv", index=False)

# In số lượng cổ phiếu từng cụm
print(df["Cluster"].value_counts().sort_index())