/* StockLens Journal — Vanilla JS, backend SQLite. Không cần npm / thư viện ngoài. */
'use strict';

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));
const byId = (id) => document.getElementById(id);

const STATUS_LABELS = {
  watch: 'Cần theo dõi thêm',
  done: 'Đã xem',
  setup: 'Mẫu hình chú ý',
  fail: 'Mẫu hình có khả năng thất bại',
  success: 'Mẫu hình khả năng thành công',
  forming: 'Có khả năng hình thành mẫu hình',
};

const state = {
  entries: [],
  statusFilter: 'all',
  search: '',
  dateScope: 'day',
  currentDate: localISODate(),
  pendingRequests: 0,
};

const noteTimers = new Map();
let toastTimeout = null;
let saveError = false;

function localISODate() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

function humanDate(iso) {
  const [y,m,d] = iso.split('-');
  return `${d}/${m}/${y}`;
}

function normalize(value) {
  return String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').toLowerCase();
}

function setSave(mode = 'saved', message) {
  const indicator = $('.save-indicator');
  indicator.classList.toggle('saving', mode === 'saving');
  indicator.classList.toggle('error', mode === 'error');

  const defaults = {
    saved: 'Tất cả thay đổi đã được lưu',
    saving: 'Đang tự động lưu...',
    error: 'Lỗi lưu dữ liệu — hãy kiểm tra máy chủ',
  };

  byId('saveState').textContent = message || defaults[mode];
}

function toast(message, error = false) {
  const el = byId('toast');
  el.textContent = message;
  el.classList.toggle('error', error);
  el.classList.add('show');
  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => el.classList.remove('show'), 3500);
}

async function request(path, options = {}) {
  let response;

  try {
    response = await fetch(path, {
      ...options,
      headers: {'Content-Type': 'application/json', ...(options.headers || {})},
    });
  } catch {
    throw new Error('Không kết nối được với máy chủ. Hãy bật lại run_windows.bat.');
  }

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error('Phản hồi từ máy chủ không hợp lệ.');
  }

  if (!response.ok) {
    throw new Error(data.error || `Lỗi máy chủ (${response.status}).`);
  }

  return data;
}

async function trackedRequest(path, options = {}) {
  state.pendingRequests++;
  setSave('saving');

  try {
    const result = await request(path, options);
    saveError = false;
    return result;
  } catch (error) {
    saveError = true;
    setSave('error');
    toast(error.message, true);
    throw error;
  } finally {
    state.pendingRequests--;

    if (!state.pendingRequests && !saveError) {
      setSave('saved');
    }
  }
}

function scopeEntries() {
  return state.entries
    .filter(entry => state.dateScope === 'all' || entry.watch_date === state.currentDate)
    .filter(entry => !state.search || normalize(`${entry.ticker} ${entry.note}`).includes(normalize(state.search)));
}

function visibleEntries() {
  return scopeEntries()
    .filter(entry => state.statusFilter === 'all' || entry.status === state.statusFilter)
    .sort((a,b) => b.watch_date.localeCompare(a.watch_date) || b.updated_at.localeCompare(a.updated_at) || b.id - a.id);
}

function fillRecordedDates() {
  const counts = new Map();

  for (const entry of state.entries) {
    counts.set(entry.watch_date, (counts.get(entry.watch_date) || 0) + 1);
  }

  const select = byId('recordedDate');
  const placeholder = make('option', '', counts.size ? 'Chọn ngày có cổ phiếu' : 'Chưa có ngày nào có cổ phiếu');
  placeholder.value = '';
  const options = [...counts.keys()].sort((a, b) => b.localeCompare(a)).map(day => {
    const option = make('option', '', `${humanDate(day)} — ${counts.get(day)} mã`);
    option.value = day;
    return option;
  });

  select.replaceChildren(placeholder, ...options);
  select.disabled = counts.size === 0;
  select.value = state.dateScope === 'day' && counts.has(state.currentDate) ? state.currentDate : '';
}

function fillStatistics() {
  const all = scopeEntries();

  const counts = {
    all: all.length,
    watch: all.filter(item => item.status === 'watch').length,
    done: all.filter(item => item.status === 'done').length,
    setup: all.filter(item => item.status === 'setup').length,
    fail: all.filter(item => item.status === 'fail').length,
    success: all.filter(item => item.status === 'success').length,
    forming: all.filter(item => item.status === 'forming').length,
  };

  byId('statAll').textContent = counts.all;
  byId('statWatch').textContent = counts.watch;
  byId('statDone').textContent = counts.done;
  byId('statSetup').textContent = counts.setup;
  byId('statFail').textContent = counts.fail;
  byId('statSuccess').textContent = counts.success;
  byId('statForming').textContent = counts.forming;

  byId('filterCountAll').textContent = counts.all;
  byId('filterCountWatch').textContent = counts.watch;
  byId('filterCountDone').textContent = counts.done;
  byId('filterCountSetup').textContent = counts.setup;
  byId('filterCountFail').textContent = counts.fail;
  byId('filterCountSuccess').textContent = counts.success;
  byId('filterCountForming').textContent = counts.forming;
}

function make(tag, className, text) {
  const node = document.createElement(tag);

  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;

  return node;
}

function removeNoteTimer(id) {
  clearTimeout(noteTimers.get(id));
  noteTimers.delete(id);
}

async function saveField(entry, field, value, redraw = false) {
  if (entry[field] === value) return;

  const previous = entry[field];
  entry[field] = value;

  if (redraw) render();

  try {
    const {entry: updated} = await trackedRequest(`/api/entries/${entry.id}`, {
      method: 'PATCH',
      body: JSON.stringify({[field]: value}),
    });

    entry.updated_at = updated.updated_at;
    entry[field] = updated[field];

    if (redraw) render();
  } catch {
    entry[field] = previous;

    if (redraw) render();
  }
}

async function saveNote(id) {
  removeNoteTimer(id);

  const entry = state.entries.find(e => e.id === id);

  if (!entry || entry.note === entry._lastSavedNote) return;

  const noteToSave = entry.note;

  try {
    const {entry: updated} = await trackedRequest(`/api/entries/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({note: noteToSave}),
      keepalive: true,
    });

    entry._lastSavedNote = noteToSave;
    entry.updated_at = updated.updated_at;

    if (entry.note !== noteToSave) {
      scheduleNoteSave(entry);
    }
  } catch {
    // Giữ nội dung chưa lưu để người dùng có thể thử lại.
  }
}

function scheduleNoteSave(entry) {
  removeNoteTimer(entry.id);
  setSave('saving');

  noteTimers.set(
    entry.id,
    setTimeout(() => saveNote(entry.id), 420)
  );
}

function flushNoteSaves() {
  for (const id of [...noteTimers.keys()]) {
    removeNoteTimer(id);
    saveNote(id);
  }
}

function makeDateCell(entry) {
  const input = make('input', 'cell-date');

  input.type = 'date';
  input.value = entry.watch_date;
  input.title = 'Nhấp để đổi ngày ghi chép';

  input.setAttribute('aria-label', `Ngày của mã ${entry.ticker}`);

  input.addEventListener('change', () => {
    if (input.value) {
      saveField(entry, 'watch_date', input.value, true);
    }
  });

  return input;
}

function makeTickerCell(entry) {
  const input = make('input', 'cell-input cell-ticker');

  input.type = 'text';
  input.value = entry.ticker;
  input.maxLength = 12;
  input.spellcheck = false;

  input.setAttribute('aria-label', 'Mã cổ phiếu');

  input.addEventListener('input', () => {
    input.value = input.value.toUpperCase();
  });

  const finish = async () => {
    const value = input.value.trim().toUpperCase();

    if (!value) {
      input.value = entry.ticker;
      return;
    }

    await saveField(entry, 'ticker', value);
    input.value = entry.ticker;
  };

  input.addEventListener('change', finish);

  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') input.blur();
  });

  return input;
}

function resizeNote(el) {
  el.style.height = 'auto';
  el.style.height = `${Math.min(Math.max(el.scrollHeight, 50), 400)}px`;
}

function makeNoteCell(entry) {
  const area = make('textarea', 'cell-note');

  area.value = entry.note;
  area.rows = 2;
  area.maxLength = 10000;
  area.placeholder = 'Viết tín hiệu, mẫu hình hoặc điều cần quan sát...';

  area.setAttribute('aria-label', `Nội dung theo dõi ${entry.ticker}`);

  area.addEventListener('input', () => {
    entry.note = area.value;
    resizeNote(area);
    scheduleNoteSave(entry);
  });

  area.addEventListener('blur', () => {
    if (noteTimers.has(entry.id)) {
      saveNote(entry.id);
    }
  });

  requestAnimationFrame(() => resizeNote(area));

  return area;
}

function makeStatusCell(entry) {
  const group = make('div', 'status-options');

  group.setAttribute('role', 'radiogroup');
  group.setAttribute('aria-label', `Tiêu chí của ${entry.ticker}`);

  for (const [value, label] of Object.entries(STATUS_LABELS)) {
    const choice = make('label', 'status-choice');
    const input = make('input');

    input.type = 'radio';
    input.name = `status-${entry.id}`;
    input.value = value;
    input.checked = entry.status === value;

    input.setAttribute('aria-label', label);

    input.addEventListener('change', () => {
      if (input.checked) {
        saveField(entry, 'status', value, true);
      }
    });

    const caption = make('span', '', label);

    choice.append(input, caption);
    group.appendChild(choice);
  }

  return group;
}

function makeDeleteCell(entry) {
  const button = make('button', 'delete-btn');

  button.type = 'button';
  button.title = `Xóa dòng ${entry.ticker} ngày ${humanDate(entry.watch_date)}`;
  button.setAttribute('aria-label', button.title);

  button.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18M8 6V4h8v2m3 0-1 14H6L5 6m5 4v7m4-7v7"/></svg>';

  button.addEventListener('click', async () => {
    if (!confirm(
      `Xóa mã ${entry.ticker} ngày ${humanDate(entry.watch_date)}?\nHành động này không thể hoàn tác.`
    )) return;

    removeNoteTimer(entry.id);

    try {
      await trackedRequest(`/api/entries/${entry.id}`, {
        method: 'DELETE'
      });

      state.entries = state.entries.filter(row => row.id !== entry.id);

      render();
      toast(`Đã xóa ${entry.ticker}.`);
    } catch {
      // trackedRequest đã hiển thị lỗi.
    }
  });

  return button;
}

function makeRow(entry) {
  const tr = make('tr', `row-${entry.status}`);

  tr.dataset.id = entry.id;

  const cells = [
    makeDateCell(entry),
    makeTickerCell(entry),
    makeNoteCell(entry),
    makeStatusCell(entry),
    makeDeleteCell(entry)
  ];

  for (const child of cells) {
    const td = document.createElement('td');

    td.appendChild(child);
    tr.appendChild(td);
  }

  return tr;
}

function render() {
  fillRecordedDates();
  fillStatistics();

  $$('.filter-pill').forEach(btn => {
    const active = btn.dataset.filter === state.statusFilter;

    btn.classList.toggle('is-active', active);
    btn.setAttribute('aria-pressed', String(active));
  });

  const rows = visibleEntries();
  const tbody = byId('entriesBody');
  const fragment = document.createDocumentFragment();

  rows.forEach(item => fragment.appendChild(makeRow(item)));

  tbody.replaceChildren(fragment);

  byId('tableCount').textContent = rows.length;
  byId('footerCount').textContent = `Đang hiển thị ${rows.length} dòng`;

  byId('emptyState').hidden = rows.length > 0;

  tbody.closest('table').hidden = rows.length === 0;

  if (!rows.length) {
    const hasEntriesInScope = scopeEntries().length > 0;

    byId('emptyMessage').textContent = hasEntriesInScope
      ? 'Không có mã nào khớp với tiêu chí đang lọc. Hãy chọn bộ lọc khác.'
      : 'Hãy thêm mã đầu tiên cho ngày đang chọn hoặc đổi sang “Tất cả ngày”.';
  }
}

async function loadEntries() {
  setSave('saving', 'Đang tải dữ liệu...');

  try {
    const result = await request('/api/entries');

    state.entries = result.entries.map(row => ({
      ...row,
      _lastSavedNote: row.note
    }));

    byId('connectionLabel').textContent = 'SQLite · lưu trên máy';
    byId('connectionDot').classList.add('is-online');

    saveError = false;
    setSave('saved');

    render();
  } catch(error) {
    byId('connectionLabel').textContent = 'Chưa kết nối máy chủ';
    byId('connectionDot').classList.remove('is-online');
    byId('recordedDate').replaceChildren(make('option', '', 'Không tải được danh sách ngày'));
    byId('recordedDate').disabled = true;

    setSave('error', 'Không tải được dữ liệu — cần khởi động server.py');

    toast(error.message, true);
  }
}

function openAddDialog() {
  const dialog = byId('entryDialog');

  byId('entryForm').reset();
  byId('inputDate').value = state.currentDate;

  dialog.showModal();
  byId('inputTicker').focus();
}

async function addEntry(event) {
  event.preventDefault();

  const ticker = byId('inputTicker').value.toUpperCase().trim();
  const watch_date = byId('inputDate').value;
  const note = byId('inputNote').value.trim();
  const status = $('#entryForm input[name="status"]:checked').value;

  if (!ticker || !watch_date) {
    toast('Hãy nhập mã cổ phiếu và ngày ghi chép.', true);
    return;
  }

  const btn = byId('saveEntryBtn');

  btn.disabled = true;

  try {
    const {entry} = await trackedRequest('/api/entries', {
      method: 'POST',
      body: JSON.stringify({
        ticker,
        watch_date,
        note,
        status
      })
    });

    state.entries.push({
      ...entry,
      _lastSavedNote: entry.note
    });

    state.currentDate = watch_date;
    state.dateScope = 'day';
    state.statusFilter = 'all';
    state.search = '';

    byId('activeDate').value = watch_date;
    byId('dateScope').value = 'day';
    byId('searchInput').value = '';

    byId('entryDialog').close();

    render();

    toast(`Đã lưu ${ticker} vào nhật ký ${humanDate(watch_date)}.`);
  } catch {
    // trackedRequest đã xử lý lỗi.
  } finally {
    btn.disabled = false;
  }
}

async function clonePreviousDay() {
  const targetDate = state.currentDate;

  try {
    const result = await trackedRequest('/api/clone', {
      method: 'POST',
      body: JSON.stringify({
        target_date: targetDate
      })
    });

    if (!result.source_date) {
      toast('Chưa có ngày ghi chép trước đó để kế thừa.');
      return;
    }

    await loadEntries();

    if (result.created) {
      toast(`Đã kế thừa ${result.created} mã từ ${humanDate(result.source_date)} sang ${humanDate(targetDate)}.`);
    } else {
      toast('Các mã của ngày trước đã có trong ngày này, không tạo trùng.');
    }
  } catch {
    // Lỗi đã được xử lý.
  }
}

function download(name, content, type) {
  const blob = new Blob([content], {type});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');

  a.href = url;
  a.download = name;
  a.click();

  setTimeout(() => URL.revokeObjectURL(url), 1500);
}

function exportJson() {
  const entries = state.entries.map(
    ({watch_date, ticker, note, status}) => ({
      watch_date,
      ticker,
      note,
      status
    })
  );

  download(
    `stocklens_sao_luu_${localISODate()}.json`,
    JSON.stringify({
      app: 'StockLens Journal',
      version: 1,
      exported_at: new Date().toISOString(),
      entries
    }, null, 2),
    'application/json;charset=utf-8'
  );

  toast(`Đã sao lưu ${entries.length} dòng vào tệp JSON.`);
}

function exportCsv() {
  const fields = [
    'Ngày',
    'Mã cổ phiếu',
    'Nội dung cần theo dõi',
    'Tiêu chí'
  ];

  const csvCell = value =>
    '"' + String(value ?? '').replace(/"/g, '""') + '"';

  const lines = [
    fields,
    ...visibleEntries().map(entry => [
      entry.watch_date,
      entry.ticker,
      entry.note,
      STATUS_LABELS[entry.status]
    ])
  ];

  const content = '\uFEFF' +
    lines.map(row => row.map(csvCell).join(';')).join('\r\n');

  download(
    `stocklens_bang_theo_doi_${localISODate()}.csv`,
    content,
    'text/csv;charset=utf-8'
  );

  toast(`Đã xuất ${lines.length - 1} dòng ra CSV để mở bằng Excel.`);
}

async function importJson(event) {
  const file = event.target.files?.[0];

  event.target.value = '';

  if (!file) return;

  try {
    const data = JSON.parse(await file.text());
    const entries = Array.isArray(data) ? data : data.entries;

    if (!Array.isArray(entries)) {
      throw new Error('Tệp phải chứa mảng entries được xuất từ StockLens.');
    }

    if (!confirm(
      `Khôi phục ${entries.length} dòng từ “${file.name}”?\n\nNhật ký hiện tại sẽ được giữ nguyên. Mã trùng ngày sẽ được bỏ qua.`
    )) return;

    const result = await trackedRequest('/api/import', {
      method: 'POST',
      body: JSON.stringify({entries})
    });

    await loadEntries();

    state.dateScope = 'all';
    byId('dateScope').value = 'all';

    render();

    toast(`Đã nhập ${result.created} dòng, bỏ qua ${result.skipped} dòng trùng.`);
  } catch(error) {
    toast(error.message, true);
  }
}

function bindEvents() {
  byId('activeDate').value = state.currentDate;

  byId('activeDate').addEventListener('change', event => {
    if (!event.target.value) return;

    flushNoteSaves();

    state.currentDate = event.target.value;

    render();
  });

  byId('recordedDate').addEventListener('change', event => {
    if (!event.target.value) return;

    flushNoteSaves();
    state.currentDate = event.target.value;
    state.dateScope = 'day';
    state.statusFilter = 'all';
    state.search = '';

    byId('activeDate').value = state.currentDate;
    byId('dateScope').value = 'day';
    byId('searchInput').value = '';
    render();
  });

  byId('dateScope').addEventListener('change', event => {
    flushNoteSaves();
    state.dateScope = event.target.value;
    render();
  });

  byId('searchInput').addEventListener('input', event => {
    flushNoteSaves();
    state.search = event.target.value;
    render();
  });

  $$('.filter-pill').forEach(button =>
    button.addEventListener('click', () => {
      flushNoteSaves();
      state.statusFilter = button.dataset.filter;
      render();
    })
  );

  byId('addEntryBtn').addEventListener('click', openAddDialog);
  byId('emptyAddBtn').addEventListener('click', openAddDialog);

  byId('closeDialogBtn').addEventListener('click', () =>
    byId('entryDialog').close()
  );

  byId('cancelDialogBtn').addEventListener('click', () =>
    byId('entryDialog').close()
  );

  byId('entryForm').addEventListener('submit', addEntry);

  byId('inputTicker').addEventListener('input', event => {
    event.target.value = event.target.value.toUpperCase();
  });

  byId('cloneBtn').addEventListener('click', clonePreviousDay);

  byId('exportJsonTop').addEventListener('click', exportJson);
  byId('exportCsvBtn').addEventListener('click', exportCsv);

  byId('importBtn').addEventListener('click', () =>
    byId('importFile').click()
  );

  byId('importFile').addEventListener('change', importJson);

  document.addEventListener('keydown', event => {
    if (
      (event.ctrlKey || event.metaKey) &&
      event.key.toLowerCase() === 'k'
    ) {
      event.preventDefault();
      byId('searchInput').focus();
    }

    if (
      (event.ctrlKey || event.metaKey) &&
      event.shiftKey &&
      event.key.toLowerCase() === 'n'
    ) {
      event.preventDefault();
      openAddDialog();
    }
  });

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) flushNoteSaves();
  });

  window.addEventListener('pagehide', flushNoteSaves);
}

bindEvents();
loadEntries();
