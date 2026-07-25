# FF7 PSX Modding — Agent Guide

Research and modding project for **Final Fantasy VII PlayStation disc images**.

## Machine split

- **This Mac (Cursor):** docs, scripts, git, planning, patch design — no disc/Ghidra/DuckStation here.
- **Windows PC:** disc images, Ghidra, DuckStation, hardware-accurate tests. Free Cursor / Composer 2.5 Fast — do not rely on that agent to invent RE steps. Shell is **Git Bash** — handoff commands must be bash-safe (forward slashes, no PowerShell/cmd).
- **Always** `git pull --ff-only` before reading or acting (`.cursor/rules/pull-and-handoff.mdc`).
- Active Windows work goes in **`docs/windows-handoff.md`**; Windows replies via **`docs/windows-results.md`** (git push) — no cross-PC paste.
- On Windows, user can ask **“what's next?”** — agent pulls, reads handoff, runs, writes results, pushes.
- If Windows Cursor is **blocked / rate-limited**, skip the agent: open `docs/windows-handoff.md` and follow it manually, then push `docs/windows-results.md` yourself.
- On Mac, user can ask **“check results”** — agent pulls and reads `docs/windows-results.md`.
- **Be autonomous:** write/push handoffs and next steps without asking; tell the user what to run on Windows.

## Start here

1. `git pull --ff-only` then `docs/windows-handoff.md` if on Windows
2. `docs/00-goals.md` — project scope
3. `docs/03-environment-setup.md` — tool checklist
4. `docs/findings/README.md` — lab notebook index
5. `.cursor/skills/record-findings/SKILL.md` — how to document discoveries

## Rules

- **Be autonomous** — act and push handoffs; tell the user what to do, don’t ask permission (`.cursor/rules/be-autonomous.mdc`)
- **Pull + handoff** — pull before acting; Windows steps in `docs/windows-handoff.md` (`.cursor/rules/pull-and-handoff.mdc`)
- **Keep repo succinct** — only material useful to other engineers (`.cursor/rules/keep-repo-succinct.mdc`)
- **Auto commit and push** when a task changes tracked files (`.cursor/rules/auto-commit-push.mdc`)
- **Capture findings** in `docs/findings/` (`.cursor/rules/capture-research-findings.mdc`)
- **No Cursor commit trailers** (`.cursor/rules/no-cursor-commit-trailers.mdc`)
- Never commit ISO/binary files
- Patch logs go in `workspace/patches/`

## Repo layout

| Path | Purpose |
|------|---------|
| `docs/windows-handoff.md` | Current Windows checklist (overwrite per task) |
| `docs/windows-results.md` | Windows → Mac outputs (git pipe) |
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
