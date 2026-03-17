"""Build script: converts '意在言先' Markdown chapters to a static HTML site with search."""

import re
import os
import json
import html as html_module
import markdown
from pathlib import Path

BOOK_DIR = Path(r"c:\Users\wan_f\Desktop\cursor\AI工作台\output\book-english-essence")
OUT_DIR = Path(r"c:\Users\wan_f\Desktop\cursor\AI工作台\book-site\docs-english-essence")
ASSETS_DIR = Path(r"c:\Users\wan_f\Desktop\cursor\AI工作台\book-site\docs")

CHAPTERS = [
    {"id": "ch00", "slug": "preface", "title_zh": "前言", "title_en": "Preface"},
    {"id": "ch01", "slug": "translation-wall", "title_zh": "第一章：翻译的墙", "title_en": "Ch1: The Translation Wall"},
    {"id": "ch02", "slug": "meaning-before-language", "title_zh": "第二章：意——语言之前的世界", "title_en": "Ch2: Meaning Before Language"},
    {"id": "ch03", "slug": "direct-link", "title_zh": "第三章：直连——从意到表达", "title_en": "Ch3: The Direct Link"},
    {"id": "ch04", "slug": "culture-skeleton", "title_zh": "第四章：文化是语义的骨架", "title_en": "Ch4: Culture as Skeleton"},
    {"id": "ch05", "slug": "input-absorbing", "title_zh": "第五章：听与读——把意吸进来", "title_en": "Ch5: Input — Absorbing"},
    {"id": "ch06", "slug": "output-expressing", "title_zh": "第六章：说与写——把意表达出去", "title_en": "Ch6: Output — Expressing"},
    {"id": "ch07", "slug": "role-of-chinese", "title_zh": "第七章：中文的正确角色", "title_en": "Ch7: Role of Chinese"},
    {"id": "ch08", "slug": "living-inside", "title_zh": "第八章：活在语言里", "title_en": "Ch8: Living Inside"},
    {"id": "ch09", "slug": "lifelong-journey", "title_zh": "第九章：终身之路", "title_en": "Ch9: The Lifelong Journey"},
]

MD_EXTENSIONS = ["tables", "fenced_code", "codehilite", "toc", "attr_list", "md_in_html"]


def convert_mermaid_blocks(html: str) -> str:
    pattern = r'<pre><code class="language-mermaid">(.*?)</code></pre>'
    replacement = r'<div class="mermaid">\1</div>'
    return re.sub(pattern, replacement, html, flags=re.DOTALL)


def fix_html_entities_in_mermaid(html: str) -> str:
    def decode_mermaid(match):
        content = match.group(1)
        content = content.replace("&amp;", "&")
        content = content.replace("&lt;", "<")
        content = content.replace("&gt;", ">")
        content = content.replace("&quot;", '"')
        content = content.replace("&#x27;", "'")
        return f'<div class="mermaid">{content}</div>'
    return re.sub(r'<div class="mermaid">(.*?)</div>', decode_mermaid, html, flags=re.DOTALL)


def build_sidebar(current_slug: str, lang: str) -> str:
    title_key = "title_zh" if lang == "zh" else "title_en"
    items = []
    for ch in CHAPTERS:
        active = "active" if ch["slug"] == current_slug else ""
        href = f'{ch["slug"]}.html?lang={lang}'
        items.append(f'<a class="nav-item {active}" href="{href}">{ch[title_key]}</a>')
    return "\n".join(items)


def build_page(chapter: dict, content_zh: str, content_en: str) -> str:
    sidebar_zh = build_sidebar(chapter["slug"], "zh")
    sidebar_en = build_sidebar(chapter["slug"], "en")

    prev_ch = None
    next_ch = None
    idx = CHAPTERS.index(chapter)
    if idx > 0:
        prev_ch = CHAPTERS[idx - 1]
    if idx < len(CHAPTERS) - 1:
        next_ch = CHAPTERS[idx + 1]

    prev_link_html = ""
    next_link_html = ""
    if prev_ch:
        prev_link_html = f'<a class="nav-btn prev" href="{prev_ch["slug"]}.html">← <span class="zh-text">{prev_ch["title_zh"]}</span><span class="en-text">{prev_ch["title_en"]}</span></a>'
    if next_ch:
        next_link_html = f'<a class="nav-btn next" href="{next_ch["slug"]}.html"><span class="zh-text">{next_ch["title_zh"]}</span><span class="en-text">{next_ch["title_en"]}</span> →</a>'

    return PAGE_TEMPLATE.format(
        title_zh=chapter["title_zh"],
        title_en=chapter["title_en"],
        sidebar_zh=sidebar_zh,
        sidebar_en=sidebar_en,
        content_zh=content_zh,
        content_en=content_en,
        prev_link=prev_link_html,
        next_link=next_link_html,
    )


PAGE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title_zh} | 意在言先</title>
<link rel="stylesheet" href="css/style.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
</head>
<body>
<div class="layout">
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-header">
      <a href="index.html" class="logo">
        <span class="logo-icon">💡</span>
        <div class="logo-text">
          <span class="zh-text">意在言先</span>
          <span class="en-text">Meaning Before Words</span>
        </div>
      </a>
    </div>
    <div style="padding:12px 16px 0;">
      <button class="search-trigger" onclick="openSearch()">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        <span class="zh-text">搜索…</span><span class="en-text">Search…</span>
        <kbd>Ctrl+K</kbd>
      </button>
    </div>
    <nav class="sidebar-nav">
      <div class="zh-text">{sidebar_zh}</div>
      <div class="en-text">{sidebar_en}</div>
    </nav>
    <div class="sidebar-footer">
      <button class="lang-toggle" onclick="toggleLang()">
        <span class="zh-text">English</span>
        <span class="en-text">中文</span>
      </button>
      <button class="theme-toggle" onclick="toggleTheme()" title="Toggle theme">◐</button>
    </div>
  </aside>
  <main class="content">
    <button class="menu-btn" onclick="toggleSidebar()">☰</button>
    <article class="chapter">
      <div class="zh-text">{content_zh}</div>
      <div class="en-text">{content_en}</div>
    </article>
    <nav class="page-nav">
      {prev_link}
      {next_link}
    </nav>
  </main>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
mermaid.initialize({{ startOnLoad: true, theme: document.body.classList.contains('light') ? 'default' : 'dark' }});
</script>
<div id="searchOverlay" class="search-overlay" onclick="if(event.target===this)closeSearch()">
  <div class="search-box">
    <div class="search-input-wrap">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
      <input id="searchInput" class="search-input" placeholder="搜索全书内容… / Search all chapters…" oninput="handleSearch(this.value)" autocomplete="off">
    </div>
    <div id="searchResults" class="search-results"></div>
  </div>
</div>
<script src="js/main.js"></script>
</body>
</html>
"""


def build_index() -> str:
    chapters_zh = []
    chapters_en = []
    for i, ch in enumerate(CHAPTERS):
        num = f"0{i}" if i < 10 else str(i)
        chapters_zh.append(f'''
        <a href="{ch['slug']}.html?lang=zh" class="chapter-card">
          <span class="chapter-num">{num}</span>
          <span class="chapter-title">{ch['title_zh']}</span>
        </a>''')
        chapters_en.append(f'''
        <a href="{ch['slug']}.html?lang=en" class="chapter-card">
          <span class="chapter-num">{num}</span>
          <span class="chapter-title">{ch['title_en']}</span>
        </a>''')

    return INDEX_TEMPLATE.format(
        chapters_zh="\n".join(chapters_zh),
        chapters_en="\n".join(chapters_en),
    )


INDEX_TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>意在言先：重新理解英语学习的本质</title>
<link rel="stylesheet" href="css/style.css">
</head>
<body>
<div class="landing">
  <header class="landing-header">
    <div class="landing-controls">
      <button class="lang-toggle" onclick="toggleLang()">
        <span class="zh-text">English</span>
        <span class="en-text">中文</span>
      </button>
      <button class="theme-toggle" onclick="toggleTheme()">◐</button>
    </div>
    <div class="hero">
      <div class="hero-icon">💡</div>
      <h1>
        <span class="zh-text">意在言先</span>
        <span class="en-text">Meaning Before Words</span>
      </h1>
      <p class="subtitle">
        <span class="zh-text">重新理解英语学习的本质</span>
        <span class="en-text">Rethinking How We Learn English</span>
      </p>
      <div class="hero-badges">
        <span class="badge">Cognitive Science</span>
        <span class="badge">9 Chapters</span>
        <span class="badge">Bilingual 中/EN</span>
        <span class="badge">25+ Theories</span>
      </div>
    </div>
  </header>

  <section class="toc-section">
    <h2>
      <span class="zh-text">📖 章节目录</span>
      <span class="en-text">📖 Table of Contents</span>
    </h2>
    <div class="chapter-grid zh-text">
{chapters_zh}
    </div>
    <div class="chapter-grid en-text">
{chapters_en}
    </div>
  </section>

  <section class="arch-section">
    <h2>
      <span class="zh-text">🧠 核心论证架构</span>
      <span class="en-text">🧠 Core Argument Architecture</span>
    </h2>
    <div class="arch-layers">
      <div class="arch-layer" style="--layer-color: #ef4444;">
        <span class="layer-num">01</span>
        <span class="zh-text">诊断 — 翻译反射为何是死胡同</span>
        <span class="en-text">Diagnosis — Why translation reflex is a dead end</span>
      </div>
      <div class="arch-layer" style="--layer-color: #f59e0b;">
        <span class="layer-num">02</span>
        <span class="zh-text">原理 — "意"先于语言存在</span>
        <span class="en-text">Principle — Yì exists before language</span>
      </div>
      <div class="arch-layer" style="--layer-color: #10b981;">
        <span class="layer-num">03</span>
        <span class="zh-text">路径 — 建立意→英文直连通路</span>
        <span class="en-text">Pathway — Build a direct yì→English link</span>
      </div>
      <div class="arch-layer" style="--layer-color: #3b82f6;">
        <span class="layer-num">04</span>
        <span class="zh-text">土壤 — 文化是语义的骨架</span>
        <span class="en-text">Soil — Culture as the semantic skeleton</span>
      </div>
      <div class="arch-layer" style="--layer-color: #8b5cf6;">
        <span class="layer-num">05–06</span>
        <span class="zh-text">策略 — 输入吸收 × 输出表达</span>
        <span class="en-text">Strategy — Input absorption × Output expression</span>
      </div>
      <div class="arch-layer" style="--layer-color: #ec4899;">
        <span class="layer-num">07–09</span>
        <span class="zh-text">实践 — 中文角色 × 沉浸生态 × 终身之路</span>
        <span class="en-text">Practice — Chinese role × Immersion × Lifelong journey</span>
      </div>
    </div>
  </section>

  <footer class="landing-footer">
    <p>
      <span class="zh-text">认知科学 × 英语学习 · 中英双语 · 25+ 理论引用</span>
      <span class="en-text">Cognitive Science × English Learning · Bilingual · 25+ Theory Citations</span>
    </p>
  </footer>
</div>
<div id="searchOverlay" class="search-overlay" onclick="if(event.target===this)closeSearch()">
  <div class="search-box">
    <div class="search-input-wrap">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
      <input id="searchInput" class="search-input" placeholder="搜索全书内容… / Search all chapters…" oninput="handleSearch(this.value)" autocomplete="off">
    </div>
    <div id="searchResults" class="search-results"></div>
  </div>
</div>
<script src="js/main.js"></script>
</body>
</html>
"""


EXTRA_CSS = """\
/* ========= SEARCH ========= */
.search-trigger {
  padding: 8px 14px; border: 1px solid var(--border); border-radius: 6px;
  background: var(--bg); color: var(--text-secondary); cursor: pointer;
  font-size: 13px; transition: all 0.2s; width: 100%; text-align: left;
  margin-bottom: 8px; display: flex; align-items: center; gap: 6px;
}
.search-trigger:hover { border-color: var(--accent); color: var(--accent); }
.search-trigger kbd {
  margin-left: auto; font-size: 11px; padding: 1px 5px;
  border: 1px solid var(--border); border-radius: 3px; opacity: 0.6;
}
.search-overlay {
  display: none; position: fixed; inset: 0; z-index: 9999;
  background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);
  justify-content: center; align-items: flex-start; padding-top: 12vh;
}
.search-overlay.active { display: flex; }
.search-box {
  width: min(560px, 90vw); background: var(--bg-secondary);
  border: 1px solid var(--border); border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.4); overflow: hidden;
}
.search-input-wrap { padding: 16px; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 10px; }
.search-input-wrap svg { flex-shrink: 0; color: var(--text-secondary); }
.search-input {
  flex: 1; background: none; border: none; outline: none;
  color: var(--text); font-size: 16px; font-family: inherit;
}
.search-input::placeholder { color: var(--text-secondary); }
.search-results { max-height: 50vh; overflow-y: auto; padding: 8px; }
.search-results:empty::after {
  content: ''; display: block; padding: 24px; text-align: center;
  color: var(--text-secondary); font-size: 14px;
}
.search-result-item {
  display: block; padding: 12px 16px; border-radius: 8px;
  text-decoration: none; color: var(--text); transition: background 0.15s;
}
.search-result-item:hover, .search-result-item.active { background: rgba(96,165,250,0.12); }
.search-result-title { font-weight: 600; font-size: 14px; margin-bottom: 4px; }
.search-result-snippet { font-size: 12px; color: var(--text-secondary); line-height: 1.5; }
.search-result-snippet mark { background: rgba(96,165,250,0.3); color: var(--text); border-radius: 2px; padding: 0 2px; }
.nav-item { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
@media (max-width: 768px) {
  .nav-item { white-space: normal; word-break: break-word; font-size: 13px; padding: 8px 16px; }
  .sidebar { width: 260px; }
  .sidebar-footer { flex-wrap: wrap; }
}
"""

SEARCH_JS = """\
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
      snippet = snippet.replace(new RegExp('(' + query.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&') + ')', 'gi'), '<mark>$1</mark>');
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
"""


def strip_html_tags(text):
    clean = re.sub(r'<[^>]+>', ' ', text)
    clean = html_module.unescape(clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def build_search_index(chapter_texts):
    index = []
    for entry in chapter_texts:
        index.append({
            "slug": entry["slug"],
            "title_zh": entry["title_zh"],
            "title_en": entry["title_en"],
            "text_zh": entry["text_zh"][:3000],
            "text_en": entry["text_en"][:3000],
        })
    return index


def main():
    os.makedirs(OUT_DIR / "css", exist_ok=True)
    os.makedirs(OUT_DIR / "js", exist_ok=True)

    css_src = ASSETS_DIR / "css" / "style.css"
    js_src = ASSETS_DIR / "js" / "main.js"

    base_css = css_src.read_text(encoding="utf-8") if css_src.exists() else ""
    base_js = js_src.read_text(encoding="utf-8") if js_src.exists() else ""

    (OUT_DIR / "css" / "style.css").write_text(base_css + "\n" + EXTRA_CSS, encoding="utf-8")
    (OUT_DIR / "js" / "main.js").write_text(base_js + "\n" + SEARCH_JS, encoding="utf-8")

    md_converter = markdown.Markdown(extensions=MD_EXTENSIONS, extension_configs={
        "codehilite": {"guess_lang": False, "use_pygments": False},
    })

    chapter_texts = []
    for chapter in CHAPTERS:
        zh_file = BOOK_DIR / f"{chapter['id']}-{chapter['slug']}-zh.md"
        en_file = BOOK_DIR / f"{chapter['id']}-{chapter['slug']}-en.md"

        zh_md = zh_file.read_text(encoding="utf-8") if zh_file.exists() else f"# {chapter['title_zh']}\n\n（章节内容待补充）"
        en_md = en_file.read_text(encoding="utf-8") if en_file.exists() else f"# {chapter['title_en']}\n\n(Chapter content coming soon)"

        md_converter.reset()
        zh_html = md_converter.convert(zh_md)
        md_converter.reset()
        en_html = md_converter.convert(en_md)

        zh_html = fix_html_entities_in_mermaid(convert_mermaid_blocks(zh_html))
        en_html = fix_html_entities_in_mermaid(convert_mermaid_blocks(en_html))

        chapter_texts.append({
            "slug": chapter["slug"],
            "title_zh": chapter["title_zh"],
            "title_en": chapter["title_en"],
            "text_zh": strip_html_tags(zh_html),
            "text_en": strip_html_tags(en_html),
        })

        page = build_page(chapter, zh_html, en_html)
        (OUT_DIR / f"{chapter['slug']}.html").write_text(page, encoding="utf-8")
        print(f"  OK {chapter['slug']}.html")

    index = build_index()
    (OUT_DIR / "index.html").write_text(index, encoding="utf-8")
    print("  OK index.html")

    si = build_search_index(chapter_texts)
    (OUT_DIR / "search-index.json").write_text(json.dumps(si, ensure_ascii=False, indent=None), encoding="utf-8")
    print("  OK search-index.json")

    (OUT_DIR / ".nojekyll").write_text("", encoding="utf-8")
    print("  OK .nojekyll")

    print(f"\nBuild complete! Output: {OUT_DIR}")


if __name__ == "__main__":
    main()
