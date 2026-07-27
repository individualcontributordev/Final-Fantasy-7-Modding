# FF7 PSX Modding — Agent guide

## How we work

- **Mac (this chat):** only agent. Give **full Windows steps in chat** — never send the user to open a handoff file for day-to-day work.
- **Windows:** human — discs, Ghidra, DuckStation, Git Bash.
- Outputs from Windows → `docs/windows-last-output.txt` + push when needed; user says **check results**.
- Never commit ISO/`.bin`. `git pull --ff-only` before acting.

## Day-to-day

Release / play steps are in the **root README**. Prefer that. Mod-specific stub notes: `mods/field-random-encounters/`.

## When guiding a Field encounter rebuild

```bash
cd /c/path/to/Final-Fantasy-7-Modding
git pull
# bump mods/field-random-encounters/VERSION if releasing
python mods/field-random-encounters/scripts/build_all_rates.py
git add builder/
git commit -m "Field encounters vX.Y.Z …"
git push
```

Needs `workspace/pristine/FINALFANTASY7_D1.bin`. After CSR base **ids** change, rebuild so `compatibleBases` match.

## RE / research

| Start | Path |
|-------|------|
| Encounter system | `docs/01-encounter-system.md` |
| Findings index | `docs/findings/README.md` |
| Ghidra | `docs/05-ghidra-guide.md` |
| Disc / Makou | `docs/02-disc-format.md` |

New findings: `docs/findings/YYYY-MM-DD-slug.md` + row in findings README (see `.cursor/skills/record-findings`).

## Rules (Cursor)

`.cursor/rules/` — mac-human-workflow, be-autonomous, keep-repo-succinct, auto-commit-push, capture-research-findings, no-cursor-commit-trailers.
