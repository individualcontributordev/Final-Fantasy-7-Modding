# FF7 PSX Modding

Research, tools, and patches for modifying **Final Fantasy VII on PlayStation** disc images — in a way that still plays on real hardware.

This repo holds reference docs, scripts, Ghidra notes, and a findings journal. Work spans field data, engine binaries (`FIELD.BIN`, `WORLD.BIN`, etc.), ISO layout, and emulator/hardware testing.

## Status

**Active — environment setup and early research.** First topic area: field encounter RNG (see below).

## Topic areas

| Area | Reference | Status |
|------|-----------|--------|
| Disc format, ISO rebuild, Makou | [docs/02-disc-format.md](docs/02-disc-format.md) | documented |
| Tooling & emulator setup | [docs/03-environment-setup.md](docs/03-environment-setup.md) | in progress |
| Patch workflow | [docs/04-workflow.md](docs/04-workflow.md) | documented |
| Ghidra / RE | [docs/05-ghidra-guide.md](docs/05-ghidra-guide.md) | in progress |
| Field encounter RNG | [docs/01-encounter-system.md](docs/01-encounter-system.md) | research (one mod idea, not project scope) |

Add new topic areas as reference docs (`docs/0N-*.md`) and findings as work expands.

## Project layout

```
ff7-modding/
├── AGENTS.md                 Cursor agent guide
├── README.md                 ← you are here
├── .cursor/
│   ├── rules/                Always-on project rules
│   └── skills/record-findings/
├── docs/
│   ├── 00-goals.md           Project scope and success criteria
│   ├── 01-encounter-system.md   (topic) Field encounter RNG
│   ├── 02-disc-format.md     ISO, FIELD.BIN, Makou save path
│   ├── 03-environment-setup.md Tool checklist — start here
│   ├── 04-workflow.md        Edit → rebuild → test loop
│   ├── 05-ghidra-guide.md    RE workflow for FIELD.BIN
│   ├── windows-handoff.md    Human Windows checklist
│   └── findings/             Dated lab notebook
├── scripts/                  FIELD.BIN decompress/recompress
└── workspace/                ISO extracts, Ghidra, patches (gitignored binaries)
```

## Research journal

Discoveries are recorded in [docs/findings/](docs/findings/README.md). The Mac Cursor agent uses
[record-findings](.cursor/skills/record-findings/SKILL.md) and
[capture-research-findings](.cursor/rules/capture-research-findings.mdc).

Human Windows steps: [docs/windows-handoff.md](docs/windows-handoff.md). Report results in the Mac chat.

## GitHub

Repo: [individualcontributordev/ff7-modding](https://github.com/individualcontributordev/ff7-modding)

After clone: `git config core.hooksPath .githooks` (strips Cursor commit trailers; see `.cursor/rules/no-cursor-commit-trailers.mdc`).

## Where to start

1. [docs/00-goals.md](docs/00-goals.md) — scope and what “done” looks like for tooling
2. [docs/03-environment-setup.md](docs/03-environment-setup.md) — install checklist
3. Extract files from a disc you own into `workspace/iso-extract/`
4. [docs/02-disc-format.md](docs/02-disc-format.md) — how the disc and save path work

## Related source repos

| Repo | Path | Role |
|------|------|------|
| Makou Reactor | `~/makoureactor` | Field editor, ISO save/rebuild |
| ff7tk | `~/ff7tk` | ISO / FIELD.BIN library (used by Makou) |

## Core idea (disc modding)

PS1 FF7 does not use the ISO directory alone for large folders like `FIELD`. Engine
binaries (`FIELD.BIN`) and per-map files (`.DAT`, `.MIM`, `.BSX`) must stay consistent
— LBAs, gzip indexes, and sector layout — for console-compatible images. Makou handles
much of that for field edits; deeper changes need `FIELD.BIN` / `WORLD.BIN` RE and patches.
