# World FORCE stub playtest (Standard) OK

**Date:** 2026-07-28  
**Confidence:** likely (feel) / confirmed (apply)  
**Related:** [world-danger](2026-07-28-world-danger.md), [world-lure-factor](2026-07-28-world-lure-factor.md)

## Apply

| Step | Result |
|------|--------|
| Patch @ `0x17DB4` | Standard (50%); head `80 1f 01 3c 20 11 22 8c` |
| Compress | zopfli **−3177** vs original → CDmage pad zeros |
| Playtest | DuckStation world grass: **fewer encounters than vanilla** |

Matches Field Standard intent: flat RCnt2 FORCE (~3.1%/check at lure 16), not vanilla Danger ramp (which gets denser the longer you walk).

## Next ship work

- Builder packs (`ic-layer-v1`) for clean + CSR bases  
- `exclusiveGroup` — likely separate from Field (`world-encounter-rate`) so both can stack  
- Optional: Light/Dense playtest
