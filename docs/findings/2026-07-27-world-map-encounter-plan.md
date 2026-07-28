# World map encounter density — research plan

**Date:** 2026-07-27  
**Confidence:** planned (public docs) / open (PS1 addresses)  
**Status:** open  
**Related:** [01-encounter-system.md](../01-encounter-system.md), [World Map RNG](https://ff7speedruns.com/index.php/World_Map_RNG), scaffold `mods/world-map-random-encounters/`

## Player-facing goal

Same Light / Standard / Dense feel as Field: flat RCnt2 FORCE chance per check (Lure-scaled), not vanilla Danger ramp — but on the **world map**.

## Architecture (not the same as Field)

| | Field (`FIELD.BIN`) | World map (`WORLD.BIN`) |
|--|---------------------|-------------------------|
| Engine file | `FIELD/FIELD.BIN` | `WORLD.BIN` (GZIPPS; same decompress as Field) |
| RNG | StepID / Offset + 256-byte table | **WorldRand** (521-byte buffer, IGT seed) |
| Danger | Field Danger `0x8007173C` | **Separate** world Danger counter (RAM TBD on PS1) |
| Check math | Danger += f(scale, rate); roll vs `(Danger × lure) >> 12` | Danger += `(lure × 16384) / encounter_rate`; battle if `WorldRand() < Danger/256` |
| Tables | Per-map `.DAT` | Region/walkmap sets (`enc_w` / in-engine data) |

Do **not** patch Field Danger or reuse Field stub offsets. Do **not** expect Makou map edits to change world density.

## Patch strategy (mirror Field)

1. Locate world encounter check (Danger += then WorldRand compare).
2. Replace Danger growth with RCnt2 FORCE stub (same densities: 25% / 50% / 75% of raw lure scale).
3. Leave formation / Yuffie / chocobo selection alone unless they share the same block.
4. Ship as separate add-on packs (`exclusiveGroup` TBD — likely can stack with Field packs; both engines load at different times).

## RE ladder

1. Extract + decompress `WORLD.BIN` → `WORLD.BIN.dec` (`scripts/decompress_gzipps.py`)
2. Align Ghidra import base with DuckStation PC on world map
3. Find `WorldSeedRand` / `WorldRand` (constant `0x5D588B65` is a strong fingerprint)
4. Xref callers → encounter check → Danger += block size
5. Stub → inject → DuckStation → MiSTer → optional burn

## Open

- [x] PS1 RAM address for world Danger = **`0x80116284`**
- [x] `WORLD.BIN` load base VA = **`0x800A0000`**
- [x] `WorldRand` / seed / scramble located
- [x] Encounter path function = **`world_encounter_check`** (`0x800B7C7C`)
- [x] Stub window `0x800B7DB4`–`0x800B7E1B` (104 bytes); patches drafted
- [x] `world_lure_factor` / `g_enemy_lure` confirmed
- [ ] Playtest stub on DuckStation
- [ ] Ship builder packs + `exclusiveGroup` decision
