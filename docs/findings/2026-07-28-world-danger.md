# world_encounter_check Danger @ 0x80116284

**Date:** 2026-07-28  
**Confidence:** confirmed  
**Related:** [world-encounter-caller](2026-07-28-world-encounter-caller.md)

## Symbols

| Symbol | VA |
|--------|-----|
| `world_encounter_check` | `0x800B7C7C` (was `FUN_800b7c7c`) |
| **`g_world_danger`** | **`0x80116284`** (word — not the Field halfword) |
| Danger += / rate path | `0x800B7DBC`–`0x800B7E18` |
| Battle `jal WorldRand` | `0x800B7E1C` |
| Compare | `0x800B7E28`–`0x800B7E38`: `WorldRand() < (g_world_danger >> 8)` |

## Math (decompiler)

```
rate = *encounter_row >> 8;
if (rate == 0)
  g_world_danger += 0x7FFF;
else
  g_world_danger += (FUN_800b7b54() << 10) / rate;   // ×1024, not ×16384 literal

if (WorldRand() < (g_world_danger >> 8) && (row & 1))
  → battle / formation path (more WorldRand calls)
```

`FUN_800b7b54` is likely lure (or lure-scaled); wiki’s `lure×16384` may be folded into that helper (`<<10` here).

## Stub target (Field-style)

Replace Danger += block **`0x800B7DBC`–`0x800B7E18`** (~`0x60` bytes), keep `jal WorldRand` @ `0x800B7E1C` and the `>>8` compare. FORCE high/zero `g_world_danger` via RCnt2 + lure so Light/Standard/Dense match Field feel.

## Open

- [ ] Confirm `FUN_800b7b54` (lure?)
- [ ] Assemble in-place FORCE stub; ship under `mods/world-map-random-encounters/`
