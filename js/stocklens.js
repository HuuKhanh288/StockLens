/* Giao diện bộ lọc StockLens — chưa có thuật toán lọc hay API giá. */
'use strict';
const form = document.getElementById('filterform');
const selectedCount = document.getElementById('selectedCount');
const overviewCount = document.getElementById('overviewCount');
const selectedTags = document.getElementById('selectedTags');
const trendReadout = document.getElementById('trendReadout');
const result = document.getElementById('result');
const filterNames = {
  ma200: 'Trên MA200',
  '69': 'Trên dao găm 69',
  '129': 'Trên dao găm 129',
  '234': 'Trên dao găm 234',
  rsi: 'Phân kỳ dương RSI',
  vol: 'Thanh khoản dưới TB 2 phiên',
};
const trendNames = {up: 'Uptrend · Xu hướng tăng', dow: 'Downtrend · Xu hướng giảm', non: 'Nontrend · Đi ngang'};

function updatePreview() {
  const selected = Array.from(form.querySelectorAll('input[name="filter"]:checked'));
  const trend = form.querySelector('input[name="trend"]:checked');
  selectedCount.textContent = selected.length;
  overviewCount.textContent = String(selected.length).padStart(2, '0');
  selectedTags.replaceChildren();
  if (selected.length === 0) {
    const placeholder = document.createElement('span');
    placeholder.className = 'placeholder';
    placeholder.textContent = 'Chưa chọn tiêu chí';
    selectedTags.append(placeholder);
  } else {
    for (const input of selected) {
      const tag = document.createElement('span');
      tag.className = 'selected-tag';
      tag.textContent = filterNames[input.value] || input.value;
      selectedTags.append(tag);
    }
  }
  trendReadout.textContent = trend ? trendNames[trend.value] : 'Chưa chọn';
}

form.addEventListener('change', updatePreview);
form.addEventListener('reset', () => {
  // reset event fires before native inputs revert to defaults.
  setTimeout(updatePreview, 0);
  result.classList.remove('notice-active');
  result.querySelector('p').textContent = 'Bộ lọc đang ở chế độ giao diện thử nghiệm. Bạn có thể chọn tiêu chí nhưng chưa có kết quả lọc.';
});
form.addEventListener('submit', (event) => {
  event.preventDefault();
  result.classList.add('notice-active');
  result.querySelector('p').textContent = 'Bạn đã chọn xong tiêu chí. StockLens hiện chưa có thuật toán lọc hoặc dữ liệu thị trường, nên chưa thể hiển thị mã cổ phiếu phù hợp.';
});
updatePreview();
