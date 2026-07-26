#!/usr/bin/env python3
"""Generate themed HTML research pages under site/research/ from articles/."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articles"
OUT = ROOT / "site" / "research"

SKIP = {"README.md", "_template.md"}

MD = markdown.Markdown(
    extensions=["tables", "fenced_code", "toc", "nl2br"],
    output_format="html5",
)

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.DOTALL)


@dataclass
class Article:
    slug: str
    title: str
    date: str
    summary: str
    order: int
    body_md: str


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, match.group(2)


def load_articles() -> list[Article]:
    articles: list[Article] = []
    for src in sorted(ARTICLES.glob("*.md")):
        if src.name in SKIP:
            continue
        meta, body = parse_frontmatter(src.read_text(encoding="utf-8"))
        title = meta.get("title") or src.stem.replace("-", " ").title()
        for line in body.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        articles.append(
            Article(
                slug=src.stem,
                title=title,
                date=meta.get("date", ""),
                summary=meta.get("summary", ""),
                order=int(meta.get("order", "99")),
                body_md=body,
            )
        )
    articles.sort(key=lambda a: (a.order, a.date, a.slug))
    return articles


def rewrite_md_links(html: str) -> str:
    def repl(match: re.Match[str]) -> str:
        href = match.group(1)
        if href.startswith(("http://", "https://", "mailto:", "#")):
            return match.group(0)
        if href.endswith(".md"):
            href = href[:-3] + ".html"
        return f'href="{href}"'

    return re.sub(r'href="([^"]+)"', repl, html)


def page_shell(title: str, body_html: str, *, crumb: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} — Final Fantasy VII Modding Research</title>
  <link rel="icon" href="../assets/meteor.png" type="image/png" />
  <link rel="stylesheet" href="../site.css" />
</head>
<body>
  <div id="space">
    <div class="stars"></div>
    <div class="stars"></div>
    <div class="stars"></div>
    <div class="stars"></div>
    <div class="stars"></div>
  </div>
  <div class="page">
    <div class="header-bar">
      <div class="nav-links">
        <a href="https://individualcontributor.dev/">Home</a>
        <a href="../">Modding</a>
        <a href="../encounter/">Encounter</a>
        <a href="./">Research</a>
        <a href="https://individualcontributor.dev/Final-Fantasy-7-CSR/">CSR</a>
        <a href="https://github.com/individualcontributordev/Final-Fantasy-7-Modding">GitHub</a>
      </div>
      <img src="../assets/meteor.png" alt="" class="site-logo" />
    </div>
    <p class="doc-nav">{crumb}</p>
    <main class="panel doc-body">
{body_html}
    </main>
    <footer class="footer">
      <p>IndividualContributor &copy; 1998</p>
    </footer>
  </div>
</body>
</html>
"""


def render_article(article: Article) -> None:
    MD.reset()
    html = MD.convert(article.body_md)
    html = rewrite_md_links(html)
    meta_bits = []
    if article.date:
        meta_bits.append(f'<time datetime="{article.date}">{article.date}</time>')
    if meta_bits:
        html = f'<p class="article-meta">{" · ".join(meta_bits)}</p>\n' + html
    crumb = f'<a href="./">Research</a> / {article.title}'
    (OUT / f"{article.slug}.html").write_text(
        page_shell(article.title, html, crumb=crumb),
        encoding="utf-8",
    )


def render_index(articles: list[Article]) -> None:
    cards = []
    for article in articles:
        summary = f"<p>{article.summary}</p>" if article.summary else ""
        date = f'<span class="article-date">{article.date}</span>' if article.date else ""
        cards.append(
            f"""      <li class="article-card">
        <a class="article-link" href="./{article.slug}.html">{article.title}</a>
        {date}
        {summary}
      </li>"""
        )
    cards_html = "\n".join(cards)
    body = f"""      <h1>Research</h1>
      <p class="lede">
        How Final Fantasy VII PlayStation mods on this site work — engine notes and packaging.
      </p>
      <ol class="article-list">
{cards_html}
      </ol>
"""
    (OUT / "index.html").write_text(
        page_shell(
            "Research",
            body,
            crumb='<a href="../">Modding</a> / Research',
        ),
        encoding="utf-8",
    )


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    articles = load_articles()
    if not articles:
        raise SystemExit(f"No articles found in {ARTICLES}")

    for article in articles:
        render_article(article)
    render_index(articles)
    print(f"Wrote {len(articles)} articles → {OUT}")


if __name__ == "__main__":
    main()
