/* Điều hướng một trang: không tải lại trang, không đổi URL. */
(() => {
  const names = ['home', 'journal', 'stocklens'];
  const buttons = [...document.querySelectorAll('[data-view]')];
  function showView(name) {
    if (!names.includes(name)) name = 'home';
    for (const item of names) {
      document.getElementById(item + '-view').hidden = item !== name;
    }
    for (const button of buttons) {
      const active = button.dataset.view === name;
      button.classList.toggle('active', active);
      if (button.closest('.shell-nav')) button.setAttribute('aria-current', active ? 'page' : 'false');
    }
    window.scrollTo({top: 0, behavior: 'instant'});
  }
  for (const button of buttons) {
    button.addEventListener('click', (event) => {
      event.preventDefault();
      showView(button.dataset.view);
    });
  }
  showView('home');
})();
