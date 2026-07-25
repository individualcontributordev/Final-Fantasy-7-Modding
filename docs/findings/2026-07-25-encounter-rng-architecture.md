# Encounter RNG architecture

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Status:** promoted → `docs/01-encounter-system.md`  
**Related:** [patch-target-field-load-reseed](2026-07-25-patch-target-field-load-reseed.md)

## Summary

Field encounter timing and formation selection use a deterministic PRNG in the **FIELD.BIN engine**, not data in per-map `.DAT` files.

## Discovery

### State variables (PS1 RAM)

| Variable | Address | Role |
|----------|---------|------|
| Danger | `0x8007173C` | 16-bit; rises while moving; resets on battle |
| StepID | `0x8009C540` | 8-bit; indexes RNG table |
| Offset | `0x8009AD2C` | 8-bit; +13 when StepID wraps |
| Formation | `0x80071C20` | 8-bit; enemy set selection |
| Step fraction | `0x8009C6D8` | Sub-step movement counter |

### RNG algorithm

```
stepid++
if stepid == 0: offset += 13
return RNG_TABLE[stepid] - offset
```

Called **twice** per encounter check (preempt + threshold). Formation uses a separate counter over the same 256-byte table.

### RNG table (first bytes)

`B1 CA EE 6C 5A 71 2E 55 D6 00 CC 99 90 6B 7D EB 4F A0 …`

### Per-map data (Makou-editable, insufficient alone)

- Encounter rate + battle tables in `.DAT` encounter section
- Field scale in `.DAT` section 1 — affects Danger growth rate only

## Why it matters

Makou cannot make encounters unpredictable. Patch target is **FIELD.BIN** (and later **WORLD.BIN** for world map).

## Sources

- [FF7 speedrun wiki — Field map encounter mechanics](https://ff7speedruns.com/index.php/Field_map_encounter_mechanics)
- TASVideos FF7 PSX submissions (StepID/Danger addresses)
- Qhimm forums topic 6431
