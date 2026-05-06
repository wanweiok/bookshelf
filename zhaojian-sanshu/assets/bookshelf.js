(function () {
  const root = document.documentElement;
  const button = document.querySelector('[data-theme-toggle]');
  const saved = localStorage.getItem('bookshelf-theme');
  if (!saved && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    root.dataset.theme = 'dark';
  }
  function syncLabel() {
    if (!button) return;
    button.textContent = root.dataset.theme === 'dark' ? '浅色模式' : '深色模式';
  }
  syncLabel();
  if (button) {
    button.addEventListener('click', function () {
      const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      root.dataset.theme = next;
      localStorage.setItem('bookshelf-theme', next);
      syncLabel();
    });
  }
})();
