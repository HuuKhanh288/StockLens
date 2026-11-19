## 1. Quy trình tính Annualized Return (CAGR)

**Mục tiêu:** Tính tốc độ tăng trưởng kép hằng năm của từng cổ phiếu dựa trên dữ liệu giá đóng cửa (Close).

### Bước 1: Lấy dữ liệu giá đóng cửa

Với mỗi cổ phiếu, lấy toàn bộ dữ liệu giá đóng cửa và sắp xếp theo thời gian từ cũ nhất đến mới nhất.

Ví dụ:

| Phiên | Ngày | Giá đóng cửa |
| :---: | :---: | :---: |
| 1 | 01/01/2020 | 20.000 |
| 2 | 02/01/2020 | 21.000 |
| ... | ... | ... |
| 1000 | 01/01/2025 | 40.000 |

### Bước 2: Xác định giá đầu kỳ và cuối kỳ

Chỉ lấy hai giá trị:
- $P_{start}$: Giá đóng cửa phiên đầu tiên.
- $P_{end}$: Giá đóng cửa phiên cuối cùng.

Ví dụ:
- $P_{start} = 20.000$
- $P_{end} = 40.000$

*Lưu ý: CAGR không sử dụng trực tiếp biến động giá của các phiên ở giữa.*

### Bước 3: Tính thời gian nắm giữ

Xác định khoảng thời gian giữa ngày đầu kỳ và cuối kỳ.

$$T = \frac{Date_{end} - Date_{start}}{365.25}$$

Trong đó:
- $T$: Thời gian nắm giữ tính bằng năm.
- $Date_{start}$: Ngày giao dịch đầu tiên.
- $Date_{end}$: Ngày giao dịch cuối cùng.

*Ví dụ: Thời gian nắm giữ khoảng 5 năm.*

### Bước 4: Tính CAGR

Áp dụng công thức:

$$\boxed{CAGR = \left(\frac{P_{end}}{P_{start}}\right)^{1/T} - 1}$$

Thay số:

$$CAGR = \left(\frac{40.000}{20.000}\right)^{1/5} - 1$$

$$\boxed{CAGR \approx 14,87\% / \text{năm}}$$

**Ý nghĩa:** Giá cổ phiếu tăng trưởng kép tương đương 14,87% mỗi năm trong giai đoạn nghiên cứu.

*(Đây không phải tỷ suất sinh lời trung bình cộng của từng năm).*
## Tại sao chia cho 365,25?

Trong công thức tính thời gian nắm giữ:

$$\boxed{T = \frac{Date_{end} - Date_{start}}{365.25}}$$

Chúng ta chia cho 365,25 để chuyển đổi khoảng thời gian từ đơn vị ngày sang năm.

**Tại sao không chia cho 365?**
- Một năm thông thường có 365 ngày.
- Một năm nhuận có 366 ngày.
- Trung bình trong chu kỳ 4 năm (giả sử có một năm nhuận):

$$\frac{365 + 365 + 365 + 366}{4} = 365.25$$

Vì vậy, sử dụng 365,25 giúp ước lượng thời gian theo năm chính xác hơn khi khoảng thời gian nghiên cứu kéo dài qua nhiều năm.
---


## 1.Quy trình tính Volatility

Giả sử cổ phiếu VCB có 1.000 phiên giao dịch.

### Bước 1: Tính tỷ suất sinh lời từng phiên

$$R_t = \frac{P_t - P_{t-1}}{P_{t-1}}$$

Ví dụ:

| Phiên | Giá đóng cửa | Tỷ suất sinh lời |
| :---: | :---: | :---: |
| 1 | 50.000 | — |
| 2 | 51.000 | +2% |
| 3 | 50.490 | -1% |
| 4 | 51.500 | +2% |
| 5 | 50.985 | -1% |

Như vậy, 1.000 phiên giá đóng cửa sẽ tạo ra 999 tỷ suất sinh lời hằng ngày.

### Bước 2: Tính tỷ suất sinh lời trung bình

Giả sử tỷ suất sinh lời của 4 phiên là:
$$R = [2\%, -1\%, 2\%, -1\%]$$

Trung bình:
$$\overline R = \frac{2 - 1 + 2 - 1}{4} = 0.5\%$$

Đến đây, bạn mới chỉ tính được tỷ suất sinh lời trung bình hằng ngày, chưa phải Volatility.

### Bước 3: Tính độ lệch chuẩn

Chúng ta cần xem tỷ suất sinh lời từng ngày lệch bao nhiêu so với mức trung bình 0,5%.

| Phiên | Return | Chênh lệch với trung bình |
| :---: | :---: | :---: |
| 1 | +2% | +1,5 điểm % |
| 2 | -1% | -1,5 điểm % |
| 3 | +2% | +1,5 điểm % |
| 4 | -1% | -1,5 điểm % |

Áp dụng công thức độ lệch chuẩn mẫu:
$$\sigma_d = \sqrt{\frac{\sum_{t=1}^{n}(R_t - \overline R)^2}{n-1}}$$

Ta được:
$$\sigma_d = \sqrt{\frac{4(1.5)^2}{3}}$$
$$\boxed{\sigma_d \approx 1.73\%}$$

Đây mới chính là Volatility hằng ngày.

## 2. Tại sao lại nhân với căn 252?

Bạn đang nhầm ở chỗ này.

$$\boxed{\sigma_{\text{annual}} = \sigma_d\sqrt{252}}$$

Thay số:
$$\sigma_{\text{annual}} = 1.73\% \times \sqrt{252}$$
$$\boxed{\sigma_{\text{annual}} \approx 27.49\%}$$

27,49% không phải tỷ suất sinh lời trung bình năm! Nó là độ biến động thường niên (Annualized Volatility).

Việc nhân với $\sqrt{252}$ dựa trên giả định phương sai lợi suất tích lũy tỷ lệ với thời gian, thường dùng khi các lợi suất hằng ngày độc lập và có phương sai ổn định.

Nếu muốn quy đổi tỷ suất sinh lời trung bình ngày sang năm theo cách tuyến tính, người ta thường nhân với 252, không phải căn 252. Nhưng đó là một chỉ tiêu khác.

---

## 3. Vậy mỗi cổ phiếu có bao nhiêu feature?

Đối với dự án K-Means của bạn, mỗi cổ phiếu sẽ có một giá trị CAGR và một giá trị Volatility.

Ví dụ:

| Ticker | CAGR | Annualized Volatility |
| :---: | :---: | :---: |
| VCB | 11,25% | 27,49% |
| FPT | 18,50% | 32,15% |
| HPG | 15,20% | 45,60% |
| VIC | -5,30% | 52,40% |

*(Số liệu minh họa)*

**Ý nghĩa:**
- **CAGR = 11,25%**: VCB có tốc độ tăng trưởng giá kép tương đương 11,25%/năm trong giai đoạn nghiên cứu.
- **Volatility = 27,49%**: Mức độ biến động của tỷ suất sinh lời VCB khi quy đổi về năm là 27,49%.

CAGR đo khả năng sinh lời, còn Volatility đo mức độ biến động.


## 3. Maximum Drawdown (MDD) – Mức sụt giảm tối đa

### 3.1. Khái niệm

Maximum Drawdown (MDD) là chỉ số đo lường mức sụt giảm lớn nhất của giá cổ phiếu từ một đỉnh xuống một đáy xuất hiện sau đỉnh đó trong giai đoạn nghiên cứu.

MDD được sử dụng để đánh giá rủi ro sụt giảm của cổ phiếu trong quá khứ.

**Lưu ý:** MDD không đơn giản là mức chênh lệch giữa giá cao nhất và giá thấp nhất trong toàn bộ dữ liệu, vì đáy phải xuất hiện sau đỉnh tương ứng.

### 3.2. Công thức tính

**Bước 1: Xác định đỉnh giá lũy kế**

Tại mỗi phiên giao dịch, xác định mức giá đóng cửa cao nhất tính từ đầu giai đoạn nghiên cứu đến phiên hiện tại.

$$Peak_t = \max(P_1, P_2, \ldots, P_t)$$

Trong đó:

- $P_t$: Giá đóng cửa tại phiên giao dịch $t$.
- $Peak_t$: Giá đóng cửa cao nhất tính đến phiên $t$.

**Bước 2: Tính Drawdown tại từng phiên**

$$DD_t = \frac{P_t - Peak_t}{Peak_t}$$

Trong đó:

- $DD_t$: Mức sụt giảm tại phiên $t$.
- $P_t$: Giá đóng cửa tại phiên $t$.
- $Peak_t$: Đỉnh giá lũy kế tại phiên $t$.

**Bước 3: Xác định Maximum Drawdown**

$$\boxed{MDD = \min_{1 \leq t \leq n}(DD_t)}$$

Trong đó $n$ là tổng số phiên giao dịch trong giai đoạn nghiên cứu.

MDD được biểu diễn dưới dạng số âm hoặc bằng 0. Giá trị càng âm thể hiện mức sụt giảm lớn nhất trong quá khứ càng sâu.

### 3.3. Quy trình tính toán

Dữ liệu đầu vào bao gồm lịch sử giá đóng cửa (`Close`) của từng cổ phiếu.

Quy trình thực hiện:

1. Đọc dữ liệu lịch sử giá cổ phiếu từ file `stock_cleaned.csv`.
2. Phân nhóm dữ liệu theo mã cổ phiếu (`Ticker`).
3. Sắp xếp các phiên giao dịch theo thời gian tăng dần (`Date`).
4. Xác định đỉnh giá đóng cửa lũy kế bằng hàm `cummax()`.
5. Tính Drawdown tại từng phiên giao dịch.
6. Sử dụng hàm `min()` để xác định Maximum Drawdown.
7. Lưu kết quả thành một đặc trưng cho mỗi cổ phiếu.

### 3.4. Ví dụ minh họa

Giả sử cổ phiếu A có dữ liệu:

| Phiên | Close | Peak | Drawdown |
|:---:|---:|---:|---:|
| 1 | 50 | 50 | 0% |
| 2 | 80 | 80 | 0% |
| 3 | 70 | 80 | -12,50% |
| 4 | 90 | 90 | 0% |
| 5 | 60 | 90 | -33,33% |
| 6 | 40 | 90 | -55,56% |
| 7 | 75 | 90 | -16,67% |

Mức sụt giảm lớn nhất xảy ra từ đỉnh 90 xuống đáy 40:

$$MDD = \frac{40 - 90}{90} \times 100\%$$

$$\boxed{MDD = -55,56\%}$$

Như vậy, cổ phiếu A từng trải qua mức sụt giảm tối đa 55,56% trong giai đoạn nghiên cứu.

### 3.5. Ý nghĩa đối với mô hình K-Means

Maximum Drawdown được sử dụng làm đặc trưng đánh giá rủi ro sụt giảm của cổ phiếu.

Khác với Annualized Volatility, vốn đo lường mức độ phân tán của tỷ suất sinh lời, Maximum Drawdown phản ánh mức tổn thất lớn nhất từ một đỉnh giá trước đó.

Việc kết hợp ba đặc trưng:

- **Annualized Return (CAGR):** Đánh giá tốc độ tăng trưởng bình quân năm.
- **Annualized Volatility:** Đánh giá mức độ biến động của tỷ suất sinh lời.
- **Maximum Drawdown:** Đánh giá mức độ sụt giảm lớn nhất trong quá khứ.

Giúp mô hình K-Means phân nhóm cổ phiếu dựa trên cả hiệu suất sinh lời và các khía cạnh khác nhau của rủi ro.

### 3.6. Lưu ý

- MDD được tính trên toàn bộ giai đoạn dữ liệu được lựa chọn.
- Khoảng thời gian từ đỉnh đến đáy tạo ra MDD không cố định.
- Sử dụng giá đóng cửa (`Close`) để bảo đảm tính nhất quán với các đặc trưng khác.
- Nên sử dụng giá đã điều chỉnh phù hợp để hạn chế sai lệch do chia tách cổ phiếu và các sự kiện doanh nghiệp.
- MDD là chỉ số rủi ro trong quá khứ, không dự báo mức sụt giảm tối đa trong tương lai.
- Khi so sánh các cổ phiếu, cần lưu ý sự khác biệt về độ dài giai đoạn dữ liệu lịch sử.

## 4. Sharpe Ratio – Tỷ suất sinh lời điều chỉnh theo rủi ro

### 4.1. Khái niệm

Sharpe Ratio là chỉ số tài chính được sử dụng để đánh giá hiệu quả sinh lời của một khoản đầu tư sau khi điều chỉnh theo mức độ rủi ro.

Chỉ số phản ánh tỷ suất sinh lời vượt mức lãi suất phi rủi ro trên mỗi đơn vị rủi ro biến động.

Sharpe Ratio càng cao, hiệu quả sinh lời trên mỗi đơn vị rủi ro càng tốt.

### 4.2. Công thức tính

Công thức tổng quát:

$$\boxed{Sharpe = \frac{R_p - R_f}{\sigma_p}}$$

Trong đó:

- $R_p$: Tỷ suất sinh lời kỳ vọng hoặc trung bình của khoản đầu tư.
- $R_f$: Lãi suất phi rủi ro.
- $\sigma_p$: Độ lệch chuẩn tỷ suất sinh lời của khoản đầu tư.

Các đại lượng phải được đo lường trên cùng một cơ sở thời gian.

**Đối với dữ liệu lịch sử giá cổ phiếu theo ngày**, Sharpe Ratio được tính như sau:

**Bước 1: Tính tỷ suất sinh lời từng phiên**

$$R_t = \frac{P_t - P_{t-1}}{P_{t-1}}$$

Trong đó:

- $P_t$: Giá đóng cửa tại phiên $t$.
- $P_{t-1}$: Giá đóng cửa phiên trước đó.
- $R_t$: Tỷ suất sinh lời tại phiên $t$.

**Bước 2: Tính tỷ suất sinh lời trung bình ngày**

$$\overline{R}_d = \frac{1}{n}\sum_{t=1}^{n}R_t$$

Trong đó $n$ là số tỷ suất sinh lời ngày hợp lệ.

**Bước 3: Tính độ lệch chuẩn tỷ suất sinh lời ngày**

$$\sigma_d = \sqrt{\frac{\sum_{t=1}^{n}(R_t - \overline{R}_d)^2}{n-1}}$$

**Bước 4: Quy đổi Sharpe Ratio về năm**

$$\boxed{Sharpe = \frac{252\overline{R}_d - R_f}{\sigma_d\sqrt{252}}}$$

Trong đó:

- $\overline{R}_d$: Tỷ suất sinh lời trung bình ngày.
- $R_f$: Lãi suất phi rủi ro theo năm, biểu diễn dưới dạng số thập phân.
- $\sigma_d$: Độ lệch chuẩn tỷ suất sinh lời ngày.
- $252$: Số phiên giao dịch giả định trong một năm.

Công thức sử dụng phương pháp thường gặp là quy đổi lợi nhuận trung bình số học và độ lệch chuẩn từ ngày sang năm.

### 4.3. Xác định lãi suất phi rủi ro

Lãi suất phi rủi ro (Risk-free Rate) là mức lợi nhuận tham chiếu của một tài sản được xem là có rủi ro vỡ nợ rất thấp.

Trong thực tế, có thể sử dụng lợi suất trái phiếu Chính phủ Việt Nam với kỳ hạn phù hợp làm đại diện.

Để đơn giản hóa quá trình xây dựng mô hình, có thể giả định:

$$R_f = 4\%/\text{năm} = 0.04$$

**Lưu ý:** Đây là giá trị giả định phục vụ thử nghiệm...


## Chuẩn hóa dữ liệu (Data Standardization)

### 1. Mục đích

Sau khi thực hiện kiểm tra và làm sạch dữ liệu, tập dữ liệu `stock_features_cleaned.csv` được sử dụng để chuẩn hóa trước khi đưa vào thuật toán K-Means.

Mục đích của quá trình chuẩn hóa là đưa các đặc trưng tài chính về cùng một thang đo, nhằm hạn chế tình trạng một đặc trưng có mức độ phân tán lớn chi phối việc tính toán khoảng cách giữa các cổ phiếu.

Việc chuẩn hóa đặc biệt quan trọng đối với K-Means vì thuật toán sử dụng khoảng cách Euclid để xác định mức độ tương đồng giữa các đối tượng.

### 2. Các đặc trưng được chuẩn hóa

Mô hình sử dụng bốn đặc trưng tài chính:

| Đặc trưng | Ý nghĩa |
| :--- | :--- |
| CAGR | Tỷ suất sinh lời kép trung bình hằng năm |
| Annualized_Volatility | Độ biến động lợi nhuận hằng năm |
| Max_Drawdown | Mức sụt giảm lớn nhất từ đỉnh xuống đáy |
| Sharpe_Ratio | Hiệu quả sinh lời sau khi điều chỉnh theo rủi ro |

Cột `Ticker` được giữ nguyên để nhận diện cổ phiếu và không tham gia quá trình chuẩn hóa.

### 3. Phương pháp chuẩn hóa

Dự án sử dụng phương pháp **Z-score Standardization**, được triển khai thông qua lớp `StandardScaler` trong thư viện Scikit-learn.

Công thức:

$$Z_i = \frac{X_i - \mu}{\sigma}$$

Trong đó:

- $X_i$: Giá trị ban đầu của đặc trưng.
- $\mu$: Giá trị trung bình của đặc trưng trên toàn bộ tập dữ liệu.
- $\sigma$: Độ lệch chuẩn của đặc trưng.
- $Z_i$: Giá trị sau chuẩn hóa.

Sau quá trình chuẩn hóa, mỗi đặc trưng có:

- Giá trị trung bình xấp xỉ 0.
- Độ lệch chuẩn xấp xỉ 1.

*StandardScaler sử dụng độ lệch chuẩn tổng thể, tương ứng với `ddof=0`.*

### 4. Lý do lựa chọn Z-score

**Thứ nhất, hạn chế sự khác biệt về thang đo giữa các đặc trưng.**

Các đặc trưng tài chính có phạm vi giá trị và mức độ phân tán khác nhau. Nếu sử dụng trực tiếp dữ liệu ban đầu, những đặc trưng có độ phân tán lớn có thể ảnh hưởng mạnh hơn đến khoảng cách Euclid.

**Thứ hai, bảo toàn sự khác biệt tương đối giữa các cổ phiếu.**

Z-score là phép biến đổi tuyến tính. Phương pháp không làm thay đổi thứ tự các giá trị trong cùng một đặc trưng.

Các cổ phiếu có giá trị cao hơn hoặc thấp hơn trung bình vẫn giữ được vị trí tương đối sau chuẩn hóa.

**Thứ ba, phù hợp với thuật toán K-Means.**

K-Means phân cụm dựa trên khoảng cách giữa các điểm dữ liệu và tâm cụm. Chuẩn hóa giúp các đặc trưng được so sánh trên thang đo thống nhất hơn.

Tuy nhiên, Z-score nhạy cảm với giá trị ngoại lai. Vì vậy, cần kiểm tra phân phối dữ liệu và đánh giá chất lượng phân cụm sau khi áp dụng thuật toán.

### 5. Quy trình thực hiện

**Bước 1:** Đọc dữ liệu từ `stock_features_cleaned.csv`.

**Bước 2:** Lựa chọn bốn đặc trưng tài chính sử dụng trong mô hình.

**Bước 3:** Khởi tạo đối tượng `StandardScaler`.

**Bước 4:** Sử dụng `fit_transform()` để tính trung bình, độ lệch chuẩn và thực hiện biến đổi dữ liệu.

**Bước 5:** Chuyển kết quả chuẩn hóa thành DataFrame và bổ sung cột `Ticker`.

**Bước 6:** Kiểm tra giá trị trung bình và độ lệch chuẩn sau chuẩn hóa.

**Bước 7:** Xuất dữ liệu thành file `stock_features_scaled.csv`.

### 6. Kết quả đầu ra

Quá trình chuẩn hóa tạo ra file:

`stock_features_scaled.csv`

File bao gồm năm cột:

| Cột | Nội dung |
| :--- | :--- |
| Ticker | Mã cổ phiếu |
| CAGR | CAGR đã chuẩn hóa |
| Annualized_Volatility | Volatility đã chuẩn hóa |
| Max_Drawdown | Max Drawdown đã chuẩn hóa |
| Sharpe_Ratio | Sharpe Ratio đã chuẩn hóa |

Dữ liệu sau chuẩn hóa được sử dụng làm đầu vào cho thuật toán K-Means.

File `stock_features_cleaned.csv` vẫn được giữ nguyên để phục vụ việc thống kê và giải thích kết quả phân cụm theo các giá trị tài chính thực tế.

### 7. Kết luận

Việc sử dụng Z-score Standardization giúp hạn chế ảnh hưởng của sự khác biệt về thang đo giữa các đặc trưng tài chính.

Đây là bước tiền xử lý quan trọng nhằm tạo điều kiện cho K-Means phân nhóm cổ phiếu dựa trên mức độ tương đồng về rủi ro và lợi nhuận.

Tuy nhiên, chuẩn hóa không loại bỏ giá trị ngoại lai và không xử lý sự tương quan giữa các đặc trưng. Chất lượng phân cụm cần được đánh giá thông qua các phương pháp như Elbow Method, Silhouette Score và phân tích đặc điểm từng cụm.