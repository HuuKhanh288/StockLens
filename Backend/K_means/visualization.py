# Trực quan hóa dữ liệu - sử dụng stock_clusters.csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# 1. Đường dẫn
BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "stock_clusters.csv"
CLEANED_FILE = BASE_DIR / "stock_features_no_outliers.csv"

OUTPUT_DIR = BASE_DIR / "charts"
OUTPUT_DIR.mkdir(exist_ok=True)

# 2. Đọc dữ liệu phân cụm
df = pd.read_csv(INPUT_FILE)

# 3. Đọc dữ liệu tài chính chưa chuẩn hóa
df_original = pd.read_csv(CLEANED_FILE)

features = [
    "CAGR",
    "Annualized_Volatility",
    "Max_Drawdown",
    "Sharpe_Ratio"
]

# 4. Ghép kết quả phân cụm với dữ liệu tài chính gốc
df_plot = df_original.merge(
    df[["Ticker", "Cluster"]],
    on="Ticker",
    how="inner",
    validate="one_to_one"
)

# Kiểm tra số lượng cổ phiếu
if len(df_plot) != len(df):
    raise ValueError("Hai file không có cùng tập mã cổ phiếu!")

# 5. Đặt tên các cụm cổ phiếu
cluster_names = {
    0: "Cổ phiếu an toàn",
    1: "Cổ phiếu tăng trưởng",
    2: "Cổ phiếu đầu cơ",
    3: "Cổ phiếu hiệu suất kém"
}

df_plot["Cluster_Name"] = df_plot["Cluster"].map(cluster_names)
# ==================================================
# BIỂU ĐỒ 1: SCATTER PLOT
# ==================================================

plt.figure(figsize=(12, 7))

sns.scatterplot(
    data=df_plot,
    x="Annualized_Volatility",
    y="CAGR",
    hue="Cluster_Name",
    palette="tab10",
    s=55,
    alpha=0.75
)

plt.title("K-Means: Stock Risk and Return")
plt.xlabel("Annualized Volatility")
plt.ylabel("CAGR")

plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "scatter_plot.png",
    dpi=300
)

plt.show()


# ==================================================
# BIỂU ĐỒ 2: SỐ LƯỢNG CỔ PHIẾU TRONG TỪNG CỤM
# ==================================================

cluster_counts = (
    df_plot["Cluster"]
    .value_counts()
    .sort_index()
)

plt.figure(figsize=(9, 6))

bars = plt.bar(
    cluster_counts.index.astype(str),
    cluster_counts.values
)

plt.title("Number of Stocks in Each Cluster")
plt.xlabel("Cluster")
plt.ylabel("Number of Stocks")

for bar in bars:
    height = bar.get_height()

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        str(int(height)),
        ha="center",
        va="bottom"
    )

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "cluster_distribution.png",
    dpi=300
)

plt.show()


# ==================================================
# BIỂU ĐỒ 3: HEATMAP ĐẶC ĐIỂM CÁC CỤM
# ==================================================

# Tính trung bình đặc trưng theo cụm
cluster_summary = (
    df_plot.groupby("Cluster")[features]
    .mean()
)

# Chuẩn hóa các giá trị trung bình để so sánh trên heatmap
# Sử dụng trung bình và độ lệch chuẩn của toàn bộ tập dữ liệu
mean_values = df_plot[features].mean()
std_values = df_plot[features].std(ddof=0)

heatmap_data = (
    cluster_summary - mean_values
) / std_values

plt.figure(figsize=(11, 6))

sns.heatmap(
    heatmap_data,
    annot=True,
    fmt=".2f",
    cmap="RdYlBu_r",
    center=0
)

plt.title("Financial Characteristics of K-Means Clusters")
plt.xlabel("Financial Features")
plt.ylabel("Cluster")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "cluster_heatmap.png",
    dpi=300
)

plt.show()


# ==================================================
# XUẤT BẢNG THỐNG KÊ CÁC CỤM
# ==================================================

cluster_summary["Stock_Count"] = cluster_counts

cluster_summary.to_csv(
    OUTPUT_DIR / "cluster_summary.csv"
)

print("\n===== THỐNG KÊ ĐẶC ĐIỂM CÁC CỤM =====")

print(cluster_summary.round(4).to_string())

print("\nĐã xuất các biểu đồ vào:", OUTPUT_DIR)