#!/usr/bin/env python3
"""Generate themed HTML research pages under site/research/ from docs/."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
FINDINGS = DOCS / "findings"
OUT = ROOT / "site" / "research"
OUT_FINDINGS = OUT / "findings"

SKIP_DOCS = {"windows-handoff.md"}
SKIP_FINDINGS = {"_template.md"}

MD = markdown.Markdown(
    extensions=["tables", "fenced_code", "toc", "nl2br"],
    output_format="html5",
)


def rewrite_md_links(html: str, *, in_findings: bool) -> str:
    """Point relative .md links at generated .html pages."""

    def repl(match: re.Match[str]) -> str:
        href = match.group(1)
        if href.startswith(("http://", "https://", "mailto:", "#")):
            return match.group(0)
        if href.endswith(".md"):
            href = href[:-3] + ".html"
        # findings pages linking to ../foo.md already become ../foo.html
        # docs pages linking to findings/foo.md become findings/foo.html
        return f'href="{href}"'

    return re.sub(r'href="([^"]+)"', repl, html)


def page_shell(
    title: str,
    body_html: str,
    *,
    depth: int,
    crumb: str,
) -> str:
    prefix = "../" * depth
    asset = prefix  # site root relative from research/ or research/findings/
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} — FF7 Modding Research</title>
  <link rel="icon" href="{asset}assets/meteor.png" type="image/png" />
  <link rel="stylesheet" href="{asset}site.css" />
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
        <a href="{asset}">Home</a>
        <a href="{asset}encounter/">Encounter</a>
        <a href="{asset}research/">Research</a>
        <a href="https://github.com/individualcontributordev/Final-Fantasy-7-Modding">GitHub</a>
      </div>
      <img src="{asset}assets/meteor.png" alt="" class="site-logo" />
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


def render_file(src: Path, dest: Path, *, in_findings: bool, depth: int, crumb: str) -> str:
    MD.reset()
    text = src.read_text(encoding="utf-8")
    html = MD.convert(text)
    html = rewrite_md_links(html, in_findings=in_findings)
    title = src.stem
    # Prefer first markdown heading as title
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        page_shell(title, html, depth=depth, crumb=crumb),
        encoding="utf-8",
    )
    return title


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    OUT_FINDINGS.mkdir(parents=True)

    topic_entries: list[tuple[str, str]] = []
    for src in sorted(DOCS.glob("*.md")):
        if src.name in SKIP_DOCS:
            continue
        title = render_file(
            src,
            OUT / f"{src.stem}.html",
            in_findings=False,
            depth=1,
            crumb='<a href="./">Research</a> / topic',
        )
        topic_entries.append((f"{src.stem}.html", title))

    finding_entries: list[tuple[str, str]] = []
    for src in sorted(FINDINGS.glob("*.md")):
        if src.name in SKIP_FINDINGS:
            continue
        title = render_file(
            src,
            OUT_FINDINGS / f"{src.stem}.html",
            in_findings=True,
            depth=2,
            crumb='<a href="../">Research</a> / <a href="./">Findings</a>',
        )
        if src.name == "README.md":
            continue
        finding_entries.append((f"findings/{src.stem}.html", title))

    topics_html = "\n".join(
        f'        <li><a href="{href}">{title}</a></li>' for href, title in topic_entries
    )
    findings_html = "\n".join(
        f'        <li><a href="{href}">{title}</a></li>' for href, title in finding_entries
    )

    index_body = f"""      <h1>Research</h1>
      <p>Reference docs and the dated findings journal for FF7 PSX modding.</p>
      <h2>Topics</h2>
      <ul>
{topics_html}
      </ul>
      <h2>Findings journal</h2>
      <ul>
{findings_html}
      </ul>
"""
    (OUT / "index.html").write_text(
        page_shell(
            "Research",
            index_body,
            depth=1,
            crumb='<a href="../">Home</a> / Research',
        ),
        encoding="utf-8",
    )
    print(f"Wrote {len(topic_entries)} topics + {len(finding_entries)} findings → {OUT}")


if __name__ == "__main__":
    main()
