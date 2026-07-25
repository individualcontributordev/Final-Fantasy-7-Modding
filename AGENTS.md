# FF7 PSX Modding — Agent Guide

Research and modding project for **Final Fantasy VII PlayStation disc images**.

## Start here

1. `docs/00-goals.md` — project scope
2. `docs/03-environment-setup.md` — tool checklist
3. `docs/findings/README.md` — lab notebook index
4. `.cursor/skills/record-findings/SKILL.md` — how to document discoveries

## Rules

- **Keep repo succinct** — only material useful to other engineers (`.cursor/rules/keep-repo-succinct.mdc`)
- **Auto commit and push** when a task changes tracked files (`.cursor/rules/auto-commit-push.mdc`)
- **Capture findings** in `docs/findings/` (`.cursor/rules/capture-research-findings.mdc`)
- **No Cursor commit trailers** (`.cursor/rules/no-cursor-commit-trailers.mdc`)
- Never commit ISO/binary files
- Patch logs go in `workspace/patches/`

## Repo layout

| Path | Purpose |
|------|---------|
| `docs/0N-*.md` | Curated reference by topic |
| `docs/findings/` | Dated journal entries |
| `scripts/` | Shared tooling (e.g. FIELD.BIN GZIPPS) |
| `workspace/iso-extract/` | Disc files (gitignored) |
| `workspace/ghidra/` | Ghidra projects |
| `workspace/patches/` | Patch attempt logs |

## External source repos

- `~/makoureactor` — field editor, ISO save
- `~/ff7tk` — ISO / FIELD.BIN library

## Topic docs today

- `01-encounter-system.md` — field encounter RNG (one active research thread)
- `02-disc-format.md` — ISO, FIELD.BIN, Makou/ff7tk
- `04-workflow.md` — edit → rebuild → test
- `05-ghidra-guide.md` — RE workflow (FIELD.BIN-focused; pattern applies elsewhere)

Add new numbered docs as new mod topics grow.
