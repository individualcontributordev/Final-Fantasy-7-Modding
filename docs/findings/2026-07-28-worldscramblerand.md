# WorldScrambleRand @ 0x800ADE30; WorldRand state @ 0x8010AE58

**Date:** 2026-07-28  
**Confidence:** confirmed  
**Related:** [worldseedrand](2026-07-28-worldseedrand.md), [worldrand-mislabel](2026-07-28-worldrand-mislabel.md)

## From end of `WorldSeedRand` (`0x800ADEA8`)

| Item | VA / note |
|------|-----------|
| Buffer fill loop | `a2 < 0x209` → `sb` to **`DAT_8010AE5C`** (= `g_world_rand_buffer`) |
| Three `jal`s | **`WorldScrambleRand`** — instr `0x0C02B78C` → **`0x800ADE30`** |
| Index init | `ori v0,0x208` then `sw` → **`DAT_8010AE58`** (= `g_world_rand_index`) |

Matches wiki: scramble×3, then `WorldRandIndex = 0x208`.

## Still open

Real **`WorldRand`** (tiny ++index / wrap / return byte) — not yet pasted. Find via xrefs to `WorldScrambleRand` or `DAT_8010AE58` (excluding seed).
