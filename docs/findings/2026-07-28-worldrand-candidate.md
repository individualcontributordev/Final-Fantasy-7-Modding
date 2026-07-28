# WorldRand candidate FUN_800adfc0

**Date:** 2026-07-28  
**Confidence:** likely  
**Related:** [worldscramblerand](2026-07-28-worldscramblerand.md)

## Evidence

`WorldScrambleRand` (`0x800ADE30`) xrefs:

| Caller | Call site |
|--------|-----------|
| `WorldSeedRand` ×3 | `0x800ADF8C` / `94` / `9C` |
| **`FUN_800adfc0`** ×1 | **`0x800ADFE8`** |

`FUN_800adfc0` sits immediately after `WorldSeedRand` (seed ends `0x800ADFBC`). That layout matches a tiny `WorldRand` sibling.

## Next

Open `0x800ADFC0`, confirm ++index / wrap `0x208` / return buffer byte, rename `WorldRand`.
