# FF7 PSX Modding — Agent guide

Part of the IndividualContributor FF7 stack. Players use **https://individualcontributor.dev/builder/** only. This repo publishes **add-on** `ic-layer-v1` packs (CDN via GitHub Pages). CSR bases live in **Final-Fantasy-7-CSR**.

## How we work

- **Mac (this chat):** only agent. Give **full Windows steps in chat** — never send the user to a handoff file for day-to-day work.
- **Windows:** human — discs, Ghidra, DuckStation, Git Bash.
- Outputs from Windows → `docs/windows-last-output.txt` + push; user says **check results**.
- Never commit ISO/`.bin`. `git pull --ff-only` before acting.
- Commits: author `individualcontributordev <contributorindividual@gmail.com>`; no Cursor trailers; auto commit/push when work lands (see `.cursor/rules/`).

## Architecture (do not regress)

| Layer | Role |
|-------|------|
| Homepage builder | UI; loads local Unmodified + remote CSR/Modding manifests |
| This repo Pages | Silent CDN: `builder/manifest.json` + pack JSON (+ redirect `index.html`) |
| `mods/<name>/` | Source of truth for a mod (VERSION, patches, scripts) |

- No PPF / RomPatcher / full-disc patcher UI.
- Field encounter rates are **named presets** (`light` / `standard` / `dense`), not free-form `%`. Pack ids still embed `25`/`50`/`75`.
- Add-ons use `exclusiveGroup: field-encounter-rate` and `compatibleBases` matching live CSR base ids.

## Day-to-day

Release / play steps: **root README**. Stub tech notes: `mods/field-random-encounters/patches/`.

```bash
# prompts Light / Standard / Dense / All unless --density is set
python mods/field-random-encounters/scripts/build_all_rates.py
# one pack:
python mods/field-random-encounters/scripts/build_on_base.py --against csr-plus --discs 1
```

Needs `workspace/pristine/FINALFANTASY7_D1.bin`. After CSR base **ids** change, rebuild so `compatibleBases` match.

## RE / research

| Start | Path |
|-------|------|
| Encounter system | `docs/01-encounter-system.md` |
| Findings index | `docs/findings/README.md` |
| Ghidra | `docs/05-ghidra-guide.md` |
| Disc / Makou | `docs/02-disc-format.md` |

New findings: `docs/findings/YYYY-MM-DD-slug.md` + row in findings README. Skill: `.cursor/skills/record-findings`. Ship packs: `.cursor/skills/ship-field-encounters`.

## Rules (Cursor)

`.cursor/rules/` — mac-human-workflow, be-autonomous, keep-repo-succinct, builder-packs, auto-commit-push, capture-research-findings, no-cursor-commit-trailers.
