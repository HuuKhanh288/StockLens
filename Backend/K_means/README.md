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