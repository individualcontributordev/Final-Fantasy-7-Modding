# Public research articles

Markdown here is what GitHub Pages publishes under `/research/`.

Private lab notes stay in `docs/` and `docs/findings/` — those are **not** built into the site.

## Add a post

1. Copy `_template.md` → `your-slug.md`
2. Fill frontmatter (`title`, `date`, `summary`, `order`)
3. Write the article
4. Locally: `python scripts/build_site_docs.py`
5. Commit and push — CI rebuilds Pages

When you ship a new mod, add a matching article here and a hub entry + patcher page under `site/`.
