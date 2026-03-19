/* Language & Theme Management */

(function () {
  const params = new URLSearchParams(window.location.search);
  const langParam = params.get("lang");

  const savedLang = langParam || localStorage.getItem("book-lang") || "zh";
  const savedTheme = localStorage.getItem("book-theme") || "dark";

  document.body.classList.add("lang-" + savedLang);
  if (savedTheme === "light") document.body.classList.add("light");

  localStorage.setItem("book-lang", savedLang);
})();

function toggleLang() {
  const isZh = document.body.classList.contains("lang-zh");
  document.body.classList.remove("lang-zh", "lang-en");
  const newLang = isZh ? "en" : "zh";
  document.body.classList.add("lang-" + newLang);
  localStorage.setItem("book-lang", newLang);

  const url = new URL(window.location);
  url.searchParams.set("lang", newLang);
  window.history.replaceState({}, "", url);
}

function toggleTheme() {
  const isLight = document.body.classList.toggle("light");
  localStorage.setItem("book-theme", isLight ? "light" : "dark");

  if (typeof mermaid !== "undefined") {
    mermaid.initialize({ theme: isLight ? "default" : "dark" });
  }
}

function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("open");
}

document.addEventListener("click", function (e) {
  const sidebar = document.getElementById("sidebar");
  const menuBtn = document.querySelector(".menu-btn");
  if (
    sidebar &&
    sidebar.classList.contains("open") &&
    !sidebar.contains(e.target) &&
    !menuBtn.contains(e.target)
  ) {
    sidebar.classList.remove("open");
  }
});

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("pre code").forEach(function (block) {
    if (
      !block.classList.contains("language-mermaid") &&
      typeof hljs !== "undefined"
    ) {
      hljs.highlightElement(block);
    }
  });
});

/* ========= CLIENT-SIDE SEARCH ========= */
let searchIndex = null;

async function loadSearchIndex() {
  if (searchIndex) return searchIndex;
  const resp = await fetch('search-index.json');
  searchIndex = await resp.json();
  return searchIndex;
}

function openSearch() {
  document.getElementById('searchOverlay').classList.add('active');
  const input = document.getElementById('searchInput');
  input.value = '';
  input.focus();
  document.getElementById('searchResults').innerHTML = '';
}

function closeSearch() {
  document.getElementById('searchOverlay').classList.remove('active');
}

document.addEventListener('keydown', function(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); openSearch(); }
  if (e.key === 'Escape') closeSearch();
});

async function handleSearch(query) {
  const results = document.getElementById('searchResults');
  if (!query || query.length < 2) { results.innerHTML = ''; return; }
  const index = await loadSearchIndex();
  const lang = document.body.classList.contains('lang-en') ? 'en' : 'zh';
  const q = query.toLowerCase();
  const matches = [];
  for (const entry of index) {
    const text = lang === 'en' ? entry.text_en : entry.text_zh;
    const title = lang === 'en' ? entry.title_en : entry.title_zh;
    const idx = text.toLowerCase().indexOf(q);
    if (idx >= 0 || title.toLowerCase().includes(q)) {
      const snippetStart = Math.max(0, idx - 40);
      const snippetEnd = Math.min(text.length, idx + query.length + 60);
      let snippet = (snippetStart > 0 ? '...' : '') + text.slice(snippetStart, snippetEnd) + (snippetEnd < text.length ? '...' : '');
      snippet = snippet.replace(new RegExp('(' + query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi'), '<mark>$1</mark>');
      matches.push({ slug: entry.slug, title, snippet, lang });
      if (matches.length >= 10) break;
    }
  }
  if (matches.length === 0) {
    results.innerHTML = '<div style="padding:24px;text-align:center;color:var(--text-secondary);font-size:14px;">' +
      (lang === 'en' ? 'No results found' : '未找到结果') + '</div>';
    return;
  }
  results.innerHTML = matches.map(m =>
    '<a class="search-result-item" href="' + m.slug + '.html?lang=' + m.lang + '">' +
    '<div class="search-result-title">' + m.title + '</div>' +
    '<div class="search-result-snippet">' + m.snippet + '</div></a>'
  ).join('');
}

/* ========= CLIENT-SIDE SEARCH ========= */
let searchIndex = null;

async function loadSearchIndex() {
  if (searchIndex) return searchIndex;
  const resp = await fetch('search-index.json');
  searchIndex = await resp.json();
  return searchIndex;
}

function openSearch() {
  document.getElementById('searchOverlay').classList.add('active');
  const input = document.getElementById('searchInput');
  input.value = '';
  input.focus();
  document.getElementById('searchResults').innerHTML = '';
}

function closeSearch() {
  document.getElementById('searchOverlay').classList.remove('active');
}

document.addEventListener('keydown', function(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); openSearch(); }
  if (e.key === 'Escape') closeSearch();
});

async function handleSearch(query) {
  const results = document.getElementById('searchResults');
  if (!query || query.length < 2) { results.innerHTML = ''; return; }
  const index = await loadSearchIndex();
  const lang = document.body.classList.contains('lang-en') ? 'en' : 'zh';
  const q = query.toLowerCase();
  const matches = [];
  for (const entry of index) {
    const text = lang === 'en' ? entry.text_en : entry.text_zh;
    const title = lang === 'en' ? entry.title_en : entry.title_zh;
    const idx = text.toLowerCase().indexOf(q);
    if (idx >= 0 || title.toLowerCase().includes(q)) {
      const snippetStart = Math.max(0, idx - 40);
      const snippetEnd = Math.min(text.length, idx + query.length + 60);
      let snippet = (snippetStart > 0 ? '...' : '') + text.slice(snippetStart, snippetEnd) + (snippetEnd < text.length ? '...' : '');
      snippet = snippet.replace(new RegExp('(' + query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi'), '<mark>$1</mark>');
      matches.push({ slug: entry.slug, title, snippet, lang });
      if (matches.length >= 10) break;
    }
  }
  if (matches.length === 0) {
    results.innerHTML = '<div style="padding:24px;text-align:center;color:var(--text-secondary);font-size:14px;">' +
      (lang === 'en' ? 'No results found' : '未找到结果') + '</div>';
    return;
  }
  results.innerHTML = matches.map(m =>
    '<a class="search-result-item" href="' + m.slug + '.html?lang=' + m.lang + '">' +
    '<div class="search-result-title">' + m.title + '</div>' +
    '<div class="search-result-snippet">' + m.snippet + '</div></a>'
  ).join('');
}
