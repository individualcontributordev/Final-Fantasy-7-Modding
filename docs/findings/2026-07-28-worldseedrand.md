# WorldSeedRand @ 0x800ADEA8

**Date:** 2026-07-28  
**Confidence:** confirmed  
**Related:** [worldseedrand-scalar-miss](2026-07-28-worldseedrand-scalar-miss.md)

## Location

| Symbol | VA | Notes |
|--------|-----|--------|
| `WorldSeedRand` | **`0x800ADEA8`** | was `FUN_800adea8` |
| multiplier load | `0x800ADEB8` / `0x800ADEBC` | `lui t0,0x5d58` + `ori t0,t0,0x8b65` |
| caller | `FUN_800b7228` @ call `0x800B736C` | likely world init / module load |

Full-word scalar search fails; halfword `0x5d58` / `0x8b65` hits work.

## Next

Find `WorldRand` (wrap at `0x208` / scramble) → xrefs → encounter Danger+= check.
