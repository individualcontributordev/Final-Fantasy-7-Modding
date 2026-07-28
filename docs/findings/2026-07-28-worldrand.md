# WorldRand @ 0x800ADFC0 confirmed

**Date:** 2026-07-28  
**Confidence:** confirmed  
**Related:** [worldrand-candidate](2026-07-28-worldrand-candidate.md), [worldscramblerand](2026-07-28-worldscramblerand.md)

## Implementation (matches wiki)

```
index++;
if (index > 0x208) { WorldScrambleRand(); index = 0; }
return buffer[index];
```

| Symbol | VA |
|--------|-----|
| `WorldRand` | **`0x800ADFC0`** |
| `g_world_rand_index` | `0x8010AE58` (`DAT_8010ae58`) |
| `g_world_rand_buffer` | `0x8010AE5C` |
| `WorldScrambleRand` | `0x800ADE30` |
| `WorldSeedRand` | `0x800ADEA8` |

~20 call sites (movement scramble, encounters, Zolom, weapons, etc.).

## Next

Find world **encounter check**: Danger += `(lure × 0x4000) / rate`, then `WorldRand() < Danger/256`. Prefer callers with **one** `jal WorldRand` near a `div` / `0x4000`.
