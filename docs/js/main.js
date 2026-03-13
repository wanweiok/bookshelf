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
