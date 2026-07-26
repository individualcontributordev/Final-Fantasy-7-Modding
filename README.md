# Final Fantasy VII PSX Modding

Research, tools, and patches for modifying **Final Fantasy VII on PlayStation** disc images — in a way that still plays on real hardware.

**Site:** https://individualcontributor.dev/Final-Fantasy-7-Modding/  
(browser patchers + public research articles)

This repo holds private lab docs, scripts, Ghidra notes, a findings journal, and the polished `articles/` that GitHub Pages publishes. Work spans field data, engine binaries (`FIELD.BIN`, `WORLD.BIN`, etc.), ISO layout, and emulator/hardware testing.

## Status

**Active — FIELD encounter FORCE stub playtested; packaging documented; public site scaffolded.** Optional next: ship encounter `.ppf`, boss preempt in-game, `WORLD.BIN`.

## Topic areas

| Area | Reference | Status |
|------|-----------|--------|
| Disc format, ISO rebuild, Makou | [docs/02-disc-format.md](docs/02-disc-format.md) | documented |
| Tooling & emulator setup | [docs/03-environment-setup.md](docs/03-environment-setup.md) | in progress |
| Patch workflow | [docs/04-workflow.md](docs/04-workflow.md) | documented |
| Ghidra / RE | [docs/05-ghidra-guide.md](docs/05-ghidra-guide.md) | in progress |
| Field encounter RNG | [docs/01-encounter-system.md](docs/01-encounter-system.md) | FIELD stub playtested |
| Combined Makou + stub PPF | [docs/06-packaging-combined-ppf.md](docs/06-packaging-combined-ppf.md) | documented |

Add new topic areas as reference docs (`docs/0N-*.md`) and findings as work expands.

## Project layout

```
Final-Fantasy-7-Modding/
├── AGENTS.md                 Cursor agent guide
├── README.md                 ← you are here
├── articles/                 public research posts (CI → site/research)
├── site/                     GitHub Pages (hub, encounter patcher, assets)
├── scripts/                  build_site_docs, make_ppf, field patch tools
├── docs/                     private guides + findings journal (not published)
└── workspace/                ISO extracts, Ghidra, patches (gitignored binaries)
```

Rebuild research HTML locally:

```bash
pip install markdown
python scripts/build_site_docs.py
```

## Research journal (private)

Dated discoveries stay in [docs/findings/](docs/findings/README.md). Public write-ups live in
[articles/](articles/README.md). The Mac Cursor agent uses
[record-findings](.cursor/skills/record-findings/SKILL.md) and
[capture-research-findings](.cursor/rules/capture-research-findings.mdc).

The Mac Cursor agent instructs in chat. Windows outputs via git:
[docs/windows-last-output.txt](docs/windows-last-output.txt) — never paste between PCs.

## GitHub

Repo: [individualcontributordev/Final-Fantasy-7-Modding](https://github.com/individualcontributordev/Final-Fantasy-7-Modding)

After clone: `git config core.hooksPath .githooks` (strips Cursor commit trailers; see `.cursor/rules/no-cursor-commit-trailers.mdc`).
