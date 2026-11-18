#dữ liệu lịch sử mà. từ khi cổ phiếu mới ipo. trước hết thì tôi muốn xứ lý. tập dữ liệu này đã.

#1. Tôi chỉ lấy dữ liệu cổ phiếu thôi. cái nào ko phải là cổ phiếu thì bỏ
#2. chỉ lấy dữ liệu 250 phiên gần nhất của cổ phiếu thôi. bộ lọc của tôi thì chưa cần quá nhiều dữ liệu lịch sử
#3. loại bỏ khỏi tập dữ liệu có trung bình giao dịch 20 phiên gần nhất <100k thì làm thế nào ? lấy công cụ nào ?
import pandas as pd

# 1. Đọc dữ liệu lịch sử
df = pd.read_csv("data/EasyStock_ToanTT_20261118.csv")
# 2. Chuẩn hóa mã chứng khoán
df["Ticker"] = df["Ticker"].astype("string").str.strip().str.upper()

# 3. Chỉ giữ mã có đúng 3 chữ cái
df = df[df["Ticker"].str.fullmatch(r"[A-Z]{3}", na=False)]

# 4. Chuẩn hóa ngày giao dịch
df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d", errors="coerce")

# Chuẩn hóa khối lượng giao dịch
df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce")

# Loại bỏ dòng lỗi ngày hoặc khối lượng
df = df.dropna(subset=["Date", "Volume"])

# Loại bỏ dữ liệu trùng mã và ngày
df = df.drop_duplicates(subset=["Ticker", "Date"], keep="last")

# 5. Sắp xếp theo mã và ngày
df = df.sort_values(["Ticker", "Date"])

# 6. Lấy 300 phiên mới nhất của mỗi cổ phiếu
# Số phiên muốn giữ
NUM_SESSIONS = None  # None = toàn bộ lịch sử, 300 = 300 phiên
# Sắp xếp ngày từ cũ đến mới
df = df.sort_values(["Ticker", "Date"])

# Giữ n phiên giao dịch gần nhất của từng cổ phiếu
if NUM_SESSIONS is not None:
    df = df.groupby("Ticker", group_keys=False).tail(NUM_SESSIONS)
# 7. Lấy 20 phiên gần nhất
last_20 = df.groupby("Ticker", group_keys=False).tail(20)

# 8. Tính khối lượng giao dịch trung bình 20 phiên
avg_volume = last_20.groupby("Ticker")["Volume"].agg(["mean", "count"])

# 9. Chỉ giữ mã đủ 20 phiên và KLGD trung bình >= 100.000
selected_stocks = avg_volume[
    (avg_volume["count"] == 20) &
    (avg_volume["mean"] >= 0)
].index

df = df[df["Ticker"].isin(selected_stocks)]

# 10. Xuất file dữ liệu đã xử lý
df.to_csv("data/stock_cleaned.csv", index=False)

print("Số cổ phiếu còn lại:", df["Ticker"].nunique())
print("Tổng số dòng dữ liệu:", len(df))
print("Đã xử lý dữ liệu thành công!")
