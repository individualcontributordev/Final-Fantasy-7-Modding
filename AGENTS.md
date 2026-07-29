# FF7 PSX Modding — Agent guide

Part of the IndividualContributor FF7 stack. Players use **https://individualcontributor.dev/builder/** only. This repo publishes **add-on** `ic-layer-v1` packs (CDN via GitHub Pages). CSR bases live in **Final-Fantasy-7-CSR**.

**Makou `FIELD/*.DAT` add-ons and CSR+ scene packs** live in the CSR repo (`ship-makou-addon`, `ship-csr-plus-scene`). **This repo** = engine/RE + encounter density packs (`research-new-mod`, `ship-field-encounters`, `ship-world-encounters`).

## How we work

- **Mac (this chat):** agent — **commits the Windows task into the repo first** (`docs/windows-last-task.md` + scripts), then a short chat pointer. Never chat-only runbooks.
- **Windows:** human — `git pull`, run COPY-PASTE from that file, paste evidence, push; discs / Ghidra / DuckStation / Git Bash.
- User says **check** → Mac pulls and reviews **repo** evidence (not live CDN unless asked).
- Never commit ISO/`.bin`. `git pull --ff-only` before acting.
- Commits: author `individualcontributordev <contributorindividual@gmail.com>`; no trailers; auto commit/push when work lands (see `.agents/rules/mac-human-workflow.mdc`).
- **Before publish:** `python scripts/verify_builder_config.py --pristine … --disc N --base … --addon …` (stacks layers like the site; required in ship skills).
- Optional built-zip smoke: `python scripts/verify_built_disc.py path/to/built.bin --disc N --base … --addon …` (same config as builder; layer payloads + stubs).

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
python mods/field-random-encounters/scripts/build_on_base.py --against csr --discs 1
```

Needs `workspace/pristine/FINALFANTASY7_D1.bin`. After CSR base **ids** change, rebuild so `compatibleBases` match.

**Live CSR bases as of 2026-07-28: `clean` (Unmodified), `csr-v0.14.1`, and
`highwind-v0.1.1` ("Highwind") — an aggressively trimmed playthrough, its
own separate mod, not a bigger CSR+.**
`csr-plus-v0.1.1` stays retired — CSR+ trims now ship as individual
`csr-plus-scene-*` add-ons from the CSR repo instead. Don't rebuild
`-on-csr-plus-*` combo packs (CSR+ base is retired); Highwind doesn't stack
with CSR+ scene add-ons either way, but field/world encounter rate packs
should still ship `-on-highwind-*` variants since Highwind is a live base.

## RE / research

| Start | Path |
|-------|------|
| **New mod (idea → builder)** | `docs/06-new-mod-research.md` |
| Encounter system | `docs/01-encounter-system.md` |
| Findings index | `docs/findings/README.md` |
| Ghidra | `docs/05-ghidra-guide.md` |
| Disc / Makou | `docs/02-disc-format.md` |
| **PS2 burn / MiSTer / hardware** | `docs/07-hardware-burn.md` |

New findings: `docs/findings/YYYY-MM-DD-slug.md` + row in findings README. Skills: `record-findings`, `research-new-mod`, `evolve-re-process`, `ship-field-encounters`.

When RE gets faster or a new surface unlocks, update `docs/06-new-mod-research.md` (Capabilities table) in the same session — rule `evolve-re-process`.

## Rules / skills layout

Canonical trees: **`.agents/rules/`**, **`.agents/skills/`** (edit here only).

Auggie also loads **`.augment/rules`** and **`.augment/skills`**, which are **symlinks** to those dirs (same pattern as other projects). Do not duplicate content under `.augment/`.

Rules include: mac-human-workflow, be-autonomous, keep-repo-succinct, builder-packs, evolve-re-process, auto-commit-push, capture-research-findings, no-cursor-commit-trailers.
