# FF7 PS1 Encounter Mod — Agent Guide

Research/mod project to make FF7 PS1 field encounters unpredictable.

## Start here

1. `docs/03-environment-setup.md` — tool checklist
2. `docs/findings/README.md` — lab notebook index
3. `.cursor/skills/record-findings/SKILL.md` — how to document discoveries

## Rules

- **Always capture findings** in `docs/findings/` (see `.cursor/rules/capture-research-findings.mdc`)
- **No Cursor commit trailers** (see `.cursor/rules/no-cursor-commit-trailers.mdc`)
- Never commit ISO/binary files
- Patch logs go in `workspace/patches/`

## Repo layout

| Path | Purpose |
|------|---------|
| `docs/0N-*.md` | Curated reference |
| `docs/findings/` | Dated journal entries |
| `scripts/` | FIELD.BIN decompress/recompress |
| `workspace/iso-extract/` | Game files (gitignored) |
| `workspace/ghidra/` | Ghidra projects |
| `workspace/patches/` | Patch attempt logs |

## External source repos

- `~/makoureactor` — field editor
- `~/ff7tk` — ISO / FIELD.BIN handling
