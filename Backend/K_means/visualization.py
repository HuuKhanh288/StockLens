"""
visualization.py - Bước 6 của quy trình K-Means: trực quan hóa kết quả phân cụm.

Đầu vào : stock_clusters.csv              - nhãn Cluster của từng mã (do Phan_cum.py tạo ra)
          stock_features_no_outliers.csv  - 4 đặc trưng ở thang đo gốc (chưa chuẩn hóa)
Đầu ra  : thư mục charts/ gồm
          scatter_plot.png, cluster_distribution.png, cluster_heatmap.png, cluster_summary.csv

Biểu đồ dùng giá trị chưa chuẩn hóa để dễ đọc (CAGR, Volatility theo đúng %).
Khi chạy có giao diện, cần đóng từng cửa sổ biểu đồ (plt.show) để script chạy tiếp.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# 1. Đường dẫn
BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "stock_clusters.csv"
# File đặc trưng gốc đã loại ngoại lai (chưa chuẩn hóa), cùng tập mã với stock_clusters.csv
CLEANED_FILE = BASE_DIR / "stock_features_no_outliers.csv"

# Thư mục lưu biểu đồ, tự tạo nếu chưa có
OUTPUT_DIR = BASE_DIR / "charts"
OUTPUT_DIR.mkdir(exist_ok=True)

# 2. Đọc dữ liệu phân cụm (đặc trưng trong file này đã bị chuẩn hóa)
df = pd.read_csv(INPUT_FILE)

# 3. Đọc dữ liệu tài chính chưa chuẩn hóa
df_original = pd.read_csv(CLEANED_FILE)

# 4 đặc trưng dùng để thống kê và vẽ biểu đồ
features = [
    "CAGR",
    "Annualized_Volatility",
    "Max_Drawdown",
    "Sharpe_Ratio"
]

# 4. Ghép nhãn Cluster vào dữ liệu tài chính gốc theo Ticker.
#    validate="one_to_one" báo lỗi nếu một mã xuất hiện nhiều lần ở bất kỳ file nào.
df_plot = df_original.merge(
    df[["Ticker", "Cluster"]],
    on="Ticker",
    how="inner",
    validate="one_to_one"
)

# Kiểm tra mọi mã trong file phân cụm đều ghép được với dữ liệu gốc
if len(df_plot) != len(df):
    raise ValueError("Hai file không có cùng tập mã cổ phiếu!")

# 5. Đặt tên các cụm cổ phiếu.
#    Tên được gán sẵn theo số hiệu cụm (xem initial_tickers trong Phan_cum.py),
#    không tự suy ra từ dữ liệu. Sau khi chạy, cần đối chiếu với cluster_summary.csv
#    để chắc chắn tên khớp với đặc điểm thực tế của từng cụm.
cluster_names = {
    0: "Cổ phiếu an toàn",
    1: "Cổ phiếu tăng trưởng",
    2: "Cổ phiếu đầu cơ",
    3: "Cổ phiếu hiệu suất kém"
}

df_plot["Cluster_Name"] = df_plot["Cluster"].map(cluster_names)

# ==================================================
# BIỂU ĐỒ 1: SCATTER PLOT RỦI RO - LỢI NHUẬN
# Trục X: độ biến động năm (rủi ro), trục Y: CAGR (lợi nhuận), màu theo cụm
# ==================================================

plt.figure(figsize=(12, 7))

sns.scatterplot(
    data=df_plot,
    x="Annualized_Volatility",
    y="CAGR",
    hue="Cluster_Name",   # Tô màu theo tên cụm
    palette="tab10",
    s=55,                 # Kích thước điểm
    alpha=0.75            # Độ trong suốt để thấy các điểm chồng nhau
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

# Đếm số mã trong mỗi cụm, sắp xếp theo số hiệu cụm 0 -> 3
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

# Ghi số lượng lên đỉnh mỗi cột
for bar in bars:
    height = bar.get_height()

    plt.text(
        bar.get_x() + bar.get_width() / 2,  # Giữa cột theo chiều ngang
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

# Trung bình 4 đặc trưng (thang đo gốc) của từng cụm
cluster_summary = (
    df_plot.groupby("Cluster")[features]
    .mean()
)

# Chuẩn hóa các giá trị trung bình để so sánh các đặc trưng trên cùng một thang màu.
# Dùng trung bình và độ lệch chuẩn tổng thể (ddof=0) của toàn bộ tập dữ liệu:
# mỗi ô cho biết trung bình của cụm lệch bao nhiêu độ lệch chuẩn so với trung bình chung
# (dương: cao hơn mức chung, âm: thấp hơn mức chung).
mean_values = df_plot[features].mean()
std_values = df_plot[features].std(ddof=0)

heatmap_data = (
    cluster_summary - mean_values
) / std_values

plt.figure(figsize=(11, 6))

sns.heatmap(
    heatmap_data,
    annot=True,        # Ghi giá trị trong từng ô
    fmt=".2f",
    cmap="RdYlBu_r",   # Đỏ: cao hơn mức chung, xanh: thấp hơn mức chung
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

# Thêm cột số lượng cổ phiếu (ghép theo số hiệu cụm qua index)
cluster_summary["Stock_Count"] = cluster_counts

# Bảng trung bình 4 đặc trưng ở thang đo gốc + số lượng mã của từng cụm
cluster_summary.to_csv(
    OUTPUT_DIR / "cluster_summary.csv"
)

print("\n===== THỐNG KÊ ĐẶC ĐIỂM CÁC CỤM =====")

print(cluster_summary.round(4).to_string())

print("\nĐã xuất các biểu đồ vào:", OUTPUT_DIR)
