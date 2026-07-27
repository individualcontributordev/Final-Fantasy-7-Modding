# New mod research (end-to-end)

How to go from “idea” → verified patch → builder pack. Field encounters are the worked example; the same loop applies to WORLD.BIN, other engines, or data mods.

## Mental model

```
Question → locate system (which file?) → RE (Ghidra + RAM)
  → smallest patch → inject → playtest → findings
  → diff vs stack base → ic-layer-v1 → builder/
```

Players never see this repo’s RE trail. They only get packs on https://individualcontributor.dev/builder/.

## What you must understand

| Layer | Why it matters | Start here |
|-------|----------------|------------|
| **Which binary** | Field engine ≠ map `.DAT` ≠ world map. Wrong file = wasted weeks. | [01](01-encounter-system.md), findings on architecture |
| **Disc / GZIPPS** | FIELD.BIN is compressed; patch `.dec`, recompress, reinsert without blowing indexes. | [02](02-disc-format.md), [04](04-workflow.md) |
| **VA alignment** | Ghidra import base must match DuckStation PCs (`FIELD` @ `0x800A0000`). | [05](05-ghidra-guide.md) |
| **Pristine vault** | Never open masters in CDmage; only copies under `workspace/iso-extract/`. | [02](02-disc-format.md) |
| **Stack bases** | Add-ons diff against **clean** or a **CSR base id**, not an arbitrary mashup. | root README, CSR Pages manifest |
| **Builder contract** | `ic-layer-v1`, `compatibleBases`, `exclusiveGroup`, short blurbs. | `.cursor/rules/builder-packs.mdc` |
| **Hardware bar** | DuckStation → MiSTer PSX → burn/PS2; EDC on real discs. | [07](07-hardware-burn.md), [03](03-environment-setup.md) |

## Research loop (Mac agent + Windows human)

1. **State the behavior** in one sentence (e.g. “fewer random field battles, Lure still works”).
2. **Pick the file** — engine (`FIELD.BIN` / `WORLD.BIN`) vs per-map data (Makou `.DAT`). Many “game feel” mods need the engine.
3. **One Windows RE task** — chat steps + `docs/windows-last-output.txt` COPY-PASTE/EVIDENCE (see `.cursor/rules/mac-human-workflow.mdc`).
4. **Record findings** — `docs/findings/YYYY-MM-DD-slug.md` immediately; promote confirmed facts to `docs/0N-*.md`.
5. **Prototype the smallest patch** — prefer in-place stubs over huge caves; keep dual `jal`s / call sites intact unless proven safe.
6. **Inject + playtest** — [04-workflow.md](04-workflow.md); DuckStation Safe Mode → **MiSTer PSX** for high-confidence logic → burn/PS2 for optical ([07-hardware-burn.md](07-hardware-burn.md)).
7. **Freeze stub bytes** under `mods/<mod>/patches/` when shipping.
8. **Ship layers** — scaffold `mods/<mod>/` (VERSION, patches, scripts), build packs for each `compatibleBases` you support, update `builder/manifest.json`.

## Scaffold for a new mod

```
mods/<mod-name>/
  VERSION
  README.md                 # one short paragraph + pointer to root README
  patches/                  # hex stubs + technical README
  scripts/                  # build_on_base-style entrypoints when ready
```

Mirror Field’s pattern: named presets if you have discrete variants; interactive CLI over cryptic free-form flags.

## Stacking rules

- **Bases** (exclusive): Unmodified / CSR / CSR+ / CSR++ — owned by CSR repo.
- **Add-ons** (this repo): must declare `compatibleBases` and usually an `exclusiveGroup` if variants conflict.
- After CSR publishes a new base **id**, rebuild add-ons.

## What Field taught (reuse)

- Confirm architecture before patching (Makou map data ≠ encounter RNG).
- Align Ghidra ↔ DuckStation before chasing xrefs.
- Prefer hardware entropy (e.g. RCnt2) over fake “random” that breaks routing tools carelessly — document tradeoffs.
- Ship density as **presets** players understand, not raw math knobs.

## Next likely targets

| Idea | Likely file | Notes |
|------|-------------|--------|
| World map encounter density | `WORLD.BIN` | Scaffold: `mods/world-map-random-encounters/` — repeat Field RE on world engine |
| Map/script tweaks | `.DAT` via Makou | Often no engine stub; still ship as layers vs chosen base |
| Other FIELD behaviors | `FIELD.BIN` | Same GZIPPS + Ghidra loop |

## Capabilities unlocked

Living list — add a row when a capability is **repeatably** usable (see skill `evolve-re-process`).

| Capability | Since | Entry |
|------------|-------|--------|
| Field encounter density packs (Light/Standard/Dense) on clean + CSR bases | 2026-07 | `mods/field-random-encounters/`, root README |
| Browser `ic-layer-v1` shipping (no PPF) | 2026-07 | builder Pages CDN |
| Mac↔Windows RE loop via `windows-last-output.txt` | 2026-07 | `.cursor/rules/mac-human-workflow.mdc` |
| Ghidra FIELD import aligned @ `0x800A0000` with DuckStation | 2026-07 | `docs/05-ghidra-guide.md` |
| Scripted on-base Field pack build (`build_on_base` / `build_all_rates`) | 2026-07 | `ship-field-encounters` skill |
| Hardware burn checklist (PS2 MechaPwn / MODE2 cue) | 2026-07 | `docs/07-hardware-burn.md` |
| ImgBurn EDC verify fail can still boot on MechaPwn PS2 | 2026-07 | CSR `notes/2026-07-27-imgburn-verify-yamada.md` |
| MiSTer PSX as pre-burn behavioral gate (Ghidra/Makou) | 2026-07 | `docs/07-hardware-burn.md` |

## Keep the process honest

When RE gets faster or a new surface opens, update **this doc** and the agent skills in the same session — do not leave breakthroughs only in chat or a single finding. Rule: `.cursor/rules/evolve-re-process.mdc`.
