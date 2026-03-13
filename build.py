"""Build script: converts Markdown book chapters to a static HTML site."""

import re
import os
import shutil
import markdown
from pathlib import Path

BOOK_DIR = Path(r"c:\Users\wan_f\Desktop\cursor\AI工作台\output\book-building-ai-agent")
OUT_DIR = Path(r"c:\Users\wan_f\Desktop\cursor\AI工作台\book-site\docs")

CHAPTERS = [
    {"id": "ch00", "slug": "preface", "title_zh": "序章：这本书能给你什么", "title_en": "Preface: What This Book Gives You"},
    {"id": "ch01", "slug": "panorama", "title_zh": "第一章：OpenClaw 全景", "title_en": "Ch1: OpenClaw Panorama"},
    {"id": "ch02", "slug": "agent-runtime", "title_zh": "第二章：Agent 运行时", "title_en": "Ch2: Agent Runtime"},
    {"id": "ch03", "slug": "memory-state", "title_zh": "第三章：记忆与状态", "title_en": "Ch3: Memory & State"},
    {"id": "ch04", "slug": "channels", "title_zh": "第四章：通信渠道", "title_en": "Ch4: Channels"},
    {"id": "ch05", "slug": "security", "title_zh": "第五章：安全与隔离", "title_en": "Ch5: Security"},
    {"id": "ch06", "slug": "scheduling", "title_zh": "第六章：调度与自主性", "title_en": "Ch6: Scheduling"},
    {"id": "ch07", "slug": "skills", "title_zh": "第七章：技能扩展", "title_en": "Ch7: Skills Extension"},
    {"id": "ch08", "slug": "assembly", "title_zh": "第八章：终章组装", "title_en": "Ch8: Assembly"},
]

MD_EXTENSIONS = ["tables", "fenced_code", "codehilite", "toc", "attr_list", "md_in_html"]


def convert_mermaid_blocks(html: str) -> str:
    """Convert <code class="language-mermaid"> blocks to <div class="mermaid">."""
    pattern = r'<pre><code class="language-mermaid">(.*?)</code></pre>'
    replacement = r'<div class="mermaid">\1</div>'
    return re.sub(pattern, replacement, html, flags=re.DOTALL)


def fix_html_entities_in_mermaid(html: str) -> str:
    """Mermaid can't parse HTML entities, so decode common ones."""
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
<title>{title_zh} | Building Your Own AI Agent</title>
<link rel="stylesheet" href="css/style.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
</head>
<body>
<div class="layout">
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-header">
      <a href="index.html" class="logo">
        <span class="logo-icon">🤖</span>
        <div class="logo-text">
          <span class="zh-text">构建你自己的 AI Agent</span>
          <span class="en-text">Building Your Own AI Agent</span>
        </div>
      </a>
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
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/python.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/yaml.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/bash.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/json.min.js"></script>
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
mermaid.initialize({{ startOnLoad: true, theme: document.body.classList.contains('light') ? 'default' : 'dark' }});
</script>
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
<title>Building Your Own AI Agent | 构建你自己的 AI Agent</title>
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
      <div class="hero-icon">🤖</div>
      <h1>
        <span class="zh-text">构建你自己的 AI Agent</span>
        <span class="en-text">Building Your Own AI Agent</span>
      </h1>
      <p class="subtitle">
        <span class="zh-text">从源码到实战，逐层拆解个人 AI 智能体架构</span>
        <span class="en-text">A Layer-by-Layer Architecture Deep Dive from Source Code to Practice</span>
      </p>
      <div class="hero-badges">
        <span class="badge">OpenClaw · 500K+ LoC</span>
        <span class="badge">NanoClaw · 2K LoC</span>
        <span class="badge">9 Chapters</span>
        <span class="badge">Bilingual 中/EN</span>
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
      <span class="zh-text">🏗️ 六层架构</span>
      <span class="en-text">🏗️ Six-Layer Architecture</span>
    </h2>
    <div class="arch-layers">
      <div class="arch-layer" style="--layer-color: #60a5fa;">
        <span class="layer-num">L1</span>
        <span class="zh-text">运行时 Runtime</span>
        <span class="en-text">Runtime</span>
      </div>
      <div class="arch-layer" style="--layer-color: #a78bfa;">
        <span class="layer-num">L2</span>
        <span class="zh-text">记忆 Memory</span>
        <span class="en-text">Memory</span>
      </div>
      <div class="arch-layer" style="--layer-color: #f472b6;">
        <span class="layer-num">L3</span>
        <span class="zh-text">通道 Channels</span>
        <span class="en-text">Channels</span>
      </div>
      <div class="arch-layer" style="--layer-color: #fb923c;">
        <span class="layer-num">L4</span>
        <span class="zh-text">安全 Security</span>
        <span class="en-text">Security</span>
      </div>
      <div class="arch-layer" style="--layer-color: #4ade80;">
        <span class="layer-num">L5</span>
        <span class="zh-text">调度 Scheduling</span>
        <span class="en-text">Scheduling</span>
      </div>
      <div class="arch-layer" style="--layer-color: #facc15;">
        <span class="layer-num">L6</span>
        <span class="zh-text">技能 Skills</span>
        <span class="en-text">Skills</span>
      </div>
    </div>
  </section>

  <footer class="landing-footer">
    <p>
      <span class="zh-text">基于 OpenClaw 开源项目 · 中英双语 · 源码驱动</span>
      <span class="en-text">Based on OpenClaw open-source project · Bilingual · Source-code driven</span>
    </p>
  </footer>
</div>
<script src="js/main.js"></script>
</body>
</html>
"""


def main():
    os.makedirs(OUT_DIR / "css", exist_ok=True)
    os.makedirs(OUT_DIR / "js", exist_ok=True)

    md_converter = markdown.Markdown(extensions=MD_EXTENSIONS, extension_configs={
        "codehilite": {"guess_lang": False, "use_pygments": False},
    })

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

        page = build_page(chapter, zh_html, en_html)
        (OUT_DIR / f"{chapter['slug']}.html").write_text(page, encoding="utf-8")
        print(f"  OK {chapter['slug']}.html")

    index = build_index()
    (OUT_DIR / "index.html").write_text(index, encoding="utf-8")
    print("  OK index.html")

    print("\nBuild complete!")


if __name__ == "__main__":
    main()
