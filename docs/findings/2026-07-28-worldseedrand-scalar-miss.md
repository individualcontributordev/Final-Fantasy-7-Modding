# WorldSeedRand: full-word scalar 0x5D588B65 not found

**Date:** 2026-07-28  
**Confidence:** confirmed (miss) / open (location)  
**Related:** [world-bin-load-base](2026-07-28-world-bin-load-base.md), [World Map RNG](https://ff7speedruns.com/index.php/World_Map_RNG)

## Evidence

Ghidra import of `WORLD.BIN.dec` @ `0x800A0000` looks correct (listing shows `"NEW "` / `"OLD "` / switch table at module start).

**Search → For Scalars** `0x5d588b65` → **0 items** (`docs/image.png`).

## Why this is expected

MIPS usually loads that constant as:

```
lui  rx, 0x5d58
ori  rx, rx, 0x8b65
```

Ghidra’s full 32-bit scalar search often **misses** split immediates (same class of issue as Field StepID `lui 0x800a` + negative offset).

## Next probes (in order)

1. **Search → Memory** hex: `65 8b 58 5d` (LE word) — if embedded as data
2. Scalar `0x5d58` and/or `0x8b65` — filter to `lui`/`ori` near a `mult`
3. Scalars `0x1e9` + `0x208` together (WorldScramble / WorldRandIndex fingerprints from wiki)
