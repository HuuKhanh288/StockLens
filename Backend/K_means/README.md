# Phân cụm cổ phiếu bằng K-Means

Thư mục `Backend/K_means` phân nhóm cổ phiếu dựa trên mức sinh lời và rủi ro trong lịch sử. Mỗi mã cổ phiếu được biểu diễn bằng bốn đặc trưng tài chính. Mô hình K-Means dùng các đặc trưng đã chuẩn hóa để chia cổ phiếu thành bốn cụm.

## Dữ liệu đầu vào

Đặt `stock_cleaned.csv` trong thư mục `Backend/K_means`. Tệp CSV cần có các cột `Ticker` (mã cổ phiếu), `Date` (ngày giao dịch, ví dụ `2025-03-03`) và `Close` (giá đóng cửa). Chuỗi giá đóng cửa cần là số dương. Tệp đầu vào nằm trong `.gitignore`, nên khi lấy mã nguồn từ Git, bạn cần chuẩn bị tệp này riêng.

Dữ liệu được sắp xếp theo mã và ngày giao dịch. Quy trình giữ các mã có ít nhất 252 bản ghi và có phiên giao dịch trùng với ngày mới nhất trong toàn bộ tập dữ liệu.

## Đặc trưng sử dụng

Ký hiệu $P_t$ là giá đóng cửa phiên $t$, $r_t = P_t / P_{t-1} - 1$ là tỷ suất sinh lời theo phiên, $\bar{r}$ là trung bình và $s_r$ là độ lệch chuẩn mẫu của tỷ suất sinh lời theo phiên. Số năm quan sát $T$ được tính bằng số ngày giữa phiên đầu và phiên cuối chia cho 365,25.

| Cột | Cách tính | Ý nghĩa |
| --- | --- | --- |
| `CAGR` | $(P_{\mathrm{cuối}} / P_{\mathrm{đầu}})^{1/T} - 1$ | Tốc độ tăng trưởng kép hằng năm của giá đóng cửa. |
| `Annualized_Volatility` | $s_r \sqrt{252}$ | Độ biến động của tỷ suất sinh lời quy đổi theo năm. |
| `Max_Drawdown` | $\min_t(P_t / \max_{i\le t} P_i - 1)$ | Mức sụt giảm lớn nhất từ một đỉnh giá đến một phiên sau đỉnh, biểu diễn bằng số âm hoặc 0. |
| `Sharpe_Ratio` | $(252\bar{r} - 0.04) / (s_r \sqrt{252})$ | Tỷ suất sinh lời vượt mức lãi suất phi rủi ro trên mỗi đơn vị biến động. Mã nguồn dùng mức giả định 4%/năm. |

## Quy trình xử lý

| Bước | Script | Đầu ra |
| --- | --- | --- |
| Tính bốn đặc trưng cho từng mã | `new_csv.py` gọi các hàm trong `feature.py` | `D:/DATA/stock_features.csv` |
| Làm sạch đặc trưng | `check_new_csv.py` bỏ dòng thiếu dữ liệu, giá trị vô hạn hoặc ngoài phạm vi, mã trùng và dòng có bất kỳ đặc trưng nào bằng 0 | `stock_features_cleaned.csv` |
| Loại ngoại lai | `remove_outliers.py` đánh dấu mã có ít nhất một đặc trưng nằm ngoài khoảng từ Q1 − 3 × IQR đến Q3 + 3 × IQR, với IQR = Q3 − Q1 | `stock_features_no_outliers.csv`, `stock_outliers_removed.csv` |
| Chuẩn hóa | `standardization.py` đưa bốn đặc trưng về thang đo Z-score bằng `StandardScaler` và giữ cột `Ticker` để nhận diện mã | `stock_features_no_outliers_scaled.csv` |
| Phân cụm | `Phan_cum.py` chạy K-Means với `n_clusters=4` và `n_init=1`. Vectơ đặc trưng đã chuẩn hóa của `ABR`, `ABI`, `VOS`, `KOS` lần lượt làm tâm khởi tạo | `stock_clusters.csv` |
| Trực quan hóa | `visualization.py` ghép nhãn cụm với đặc trưng trước chuẩn hóa qua `Ticker` | Ba biểu đồ PNG và một bảng tổng hợp trong `charts/` |

## Cách chạy trên Windows

Mở PowerShell ở thư mục gốc của StockLens và chạy lần lượt. `new_csv.py` hiện ghi vào `D:\DATA`, nên tài khoản chạy script cần có quyền ghi vào đó. Lệnh `Copy-Item` đưa CSV về thư mục mà `check_new_csv.py` đọc.

```powershell
Set-Location .\Backend\K_means
python -m pip install pandas numpy scikit-learn matplotlib seaborn

python new_csv.py
Copy-Item -LiteralPath 'D:\DATA\stock_features.csv' -Destination '.\stock_features.csv'
python check_new_csv.py
python remove_outliers.py
python standardization.py
python Phan_cum.py
python visualization.py
```

Nếu bạn đã có `stock_features.csv` trong thư mục `K_means`, có thể chạy từ `check_new_csv.py`. Khi dùng tập dữ liệu khác, bốn mã dùng làm tâm khởi tạo phải còn trong dữ liệu sau tiền xử lý. Nếu thiếu mã, hãy cập nhật `initial_tickers` trong `Phan_cum.py` thành bốn mã có trong `stock_features_no_outliers_scaled.csv`.

Có thể chạy riêng `python feature.py` và nhập mã cổ phiếu để xem các chỉ số trên terminal. Khi chạy `visualization.py` với giao diện đồ họa, đóng từng cửa sổ biểu đồ để script tiếp tục.

## Kết quả

- `stock_clusters.csv` chứa mỗi mã cổ phiếu, bốn đặc trưng đã chuẩn hóa và nhãn `Cluster` từ 0 đến 3.
- `charts/scatter_plot.png` biểu diễn CAGR theo độ biến động hằng năm và tô màu theo cụm.
- `charts/cluster_distribution.png` cho biết số lượng cổ phiếu trong từng cụm.
- `charts/cluster_heatmap.png` cho thấy trung bình của từng đặc trưng trong mỗi cụm lệch bao nhiêu độ lệch chuẩn so với trung bình chung.
- `charts/cluster_summary.csv` chứa số lượng cổ phiếu và giá trị trung bình của bốn đặc trưng theo cụm trên thang đo ban đầu.

Tên cụm trên biểu đồ phân tán được gán sẵn trong `visualization.py`. Dùng bảng `cluster_summary.csv` để đối chiếu các tên này với đặc điểm của từng cụm sau khi chạy.
