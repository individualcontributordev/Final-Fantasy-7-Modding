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
| **Builder contract** | `ic-layer-v1`, `compatibleBases`, `exclusiveGroup`, short blurbs. | [docs/reference/layer-engineering.md](reference/layer-engineering.md) |
| **Hardware bar** | DuckStation → MiSTer PSX → burn/PS2; EDC on real discs. | [07](07-hardware-burn.md), [03](03-environment-setup.md) |

## Research loop

1. **State the behavior** in one sentence (e.g. “fewer random field battles, Lure still works”).
2. **Pick the file** — engine (`FIELD.BIN` / `WORLD.BIN`) vs per-map data (Makou `.DAT`). Many “game feel” mods need the engine. **Makou FIELD packs / CSR+ scenes → Final-Fantasy-7-CSR** (`ship-makou-addon`, `ship-csr-plus-scene`); continue here only for engine/RE work.
3. **One RE task at a time** — verify each claim (bytes, source, or a live emulator test) before moving to the next.
4. **Record findings** — write down offsets/bytes/results as you go; promote confirmed facts into the relevant `docs/0N-*.md`.
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

- **Bases** (exclusive): Unmodified / CSR / Highwind — owned by CSR repo. CSR+ is no longer a base; its trims are `csr-plus-scene-*` add-ons on top of CSR.
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
| Ghidra FIELD import aligned @ `0x800A0000` with DuckStation | 2026-07 | `docs/05-ghidra-guide.md` |
| Scripted on-base Field pack build (`build_on_base` / `build_all_rates`) | 2026-07 | `ship-field-encounters` skill |
| Hardware burn checklist (PS2 MechaPwn / MODE2 cue) | 2026-07 | `docs/07-hardware-burn.md` |
| ImgBurn EDC verify fail can still boot on MechaPwn PS2 | 2026-07 | CSR `notes/2026-07-27-imgburn-verify-yamada.md` |
| MiSTer PSX as pre-burn behavioral gate (Ghidra/Makou) | 2026-07 | `docs/07-hardware-burn.md` |
| Builder EDC repair → ImgBurn → PS2 fields load (CSR+ D1) | 2026-07 | CSR `notes/2026-07-27-imgburn-verify-yamada.md` |
| Single-disc on CSR (Ask + SNOVA + field trims + manip movies) | 2026-08 | `mods/single-disc/`, skill `ship-single-disc` |
| FIELD DAT structured compare (LZS, opcodes, text pad vs content) | 2026-08 | `scripts/compare_field_dat.py` |
| Multi-disc CSR FIELD collisions catalogued (10 D1+D2) | 2026-08 | `docs/findings/field-collisions-2026-08-06/` |
| Absolute CD LBA movie seek (LOSLAKE1 / CANONON alias) | 2026-08 | `docs/findings/2026-08-05-loslake1-cdrom-d1-vs-d2.md` |

## Keep the process honest

When RE gets faster or a new surface opens, update **this doc** in the same
session — do not leave breakthroughs undocumented.
