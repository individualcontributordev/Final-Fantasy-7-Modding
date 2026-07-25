# FF7 PSX Modding — Agent Guide

Research and modding project for **Final Fantasy VII PlayStation disc images**.

## Workflow

- **Mac Cursor (this chat):** only agent. Gives **full instructions in chat**.
- **Windows:** human only — disc, Ghidra, DuckStation, Git Bash.
- **Never** tell the user to open/read `docs/windows-handoff.md` for steps.
- **Never** ask to paste across PCs. Outputs → `docs/windows-last-output.txt` + push → user says **check results**.
- Mac may install helper tools; **not** DuckStation or Ghidra.
- Always `git pull --ff-only` before acting (`.cursor/rules/mac-human-workflow.mdc`).

## Start here (agent)

1. `docs/00-goals.md` — project scope
2. `docs/03-environment-setup.md` — tool checklist
3. `docs/findings/README.md` — lab notebook index
4. `docs/05-ghidra-guide.md` — RE reference

## Rules

- **Mac/human workflow** (`.cursor/rules/mac-human-workflow.mdc`) — instruct in chat
- **Be autonomous** (`.cursor/rules/be-autonomous.mdc`)
- **Keep repo succinct** (`.cursor/rules/keep-repo-succinct.mdc`)
- **Auto commit and push** (`.cursor/rules/auto-commit-push.mdc`)
- **Capture findings** (`.cursor/rules/capture-research-findings.mdc`)
- **No Cursor commit trailers** (`.cursor/rules/no-cursor-commit-trailers.mdc`)
- Never commit ISO/binary files

## Repo layout

| Path | Purpose |
|------|---------|
| `docs/windows-last-output.txt` | Latest Windows command output (git pipe) |
| `docs/0N-*.md` | Curated reference by topic |
| `docs/findings/` | Dated journal entries |
| `scripts/` | Shared tooling |
| `workspace/` | Local disc/Ghidra/patches (gitignored binaries) |

## Topic docs

- `01-encounter-system.md` — field encounter RNG
- `02-disc-format.md` — ISO, FIELD.BIN, Makou/ff7tk
- `04-workflow.md` — edit → rebuild → test
- `05-ghidra-guide.md` — RE workflow
