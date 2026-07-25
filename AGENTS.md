# FF7 PSX Modding — Agent Guide

Research and modding project for **Final Fantasy VII PlayStation disc images**.

## Workflow

- **Mac Cursor (this chat):** only agent — docs, scripts, planning, analysis.
- **Windows:** human only — disc, Ghidra, DuckStation, Git Bash. No Windows Cursor agent.
- User talks **only in this chat**. Agent tells them what to do; durable steps in `docs/windows-handoff.md`.
- **Default:** user reports results in chat; agent updates the repo.
- **Git push from Windows:** only when the agent needs a specific file to analyze (not routine checklists).
- Mac may install helper tools; **not** DuckStation or Ghidra.
- Always `git pull --ff-only` before acting (`.cursor/rules/mac-human-workflow.mdc`).

## Start here

1. `docs/windows-handoff.md` — current human checklist (if active)
2. `docs/00-goals.md` — project scope
3. `docs/03-environment-setup.md` — tool checklist
4. `docs/findings/README.md` — lab notebook index

## Rules

- **Mac/human workflow** (`.cursor/rules/mac-human-workflow.mdc`)
- **Be autonomous** (`.cursor/rules/be-autonomous.mdc`)
- **Keep repo succinct** (`.cursor/rules/keep-repo-succinct.mdc`)
- **Auto commit and push** (`.cursor/rules/auto-commit-push.mdc`)
- **Capture findings** (`.cursor/rules/capture-research-findings.mdc`)
- **No Cursor commit trailers** (`.cursor/rules/no-cursor-commit-trailers.mdc`)
- Never commit ISO/binary files
- Patch logs go in `workspace/patches/`

## Repo layout

| Path | Purpose |
|------|---------|
| `docs/windows-handoff.md` | Current checklist for the human on Windows |
| `docs/0N-*.md` | Curated reference by topic |
| `docs/findings/` | Dated journal entries |
| `scripts/` | Shared tooling (e.g. FIELD.BIN GZIPPS) |
| `workspace/iso-extract/` | Disc files (gitignored) |
| `workspace/ghidra/` | Ghidra projects (local) |
| `workspace/patches/` | Patch attempt logs |

## External source repos

- `~/makoureactor` — field editor, ISO save
- `~/ff7tk` — ISO / FIELD.BIN library

## Topic docs today

- `01-encounter-system.md` — field encounter RNG (one active research thread)
- `02-disc-format.md` — ISO, FIELD.BIN, Makou/ff7tk
- `04-workflow.md` — edit → rebuild → test
- `05-ghidra-guide.md` — RE workflow (FIELD.BIN-focused; pattern applies elsewhere)
