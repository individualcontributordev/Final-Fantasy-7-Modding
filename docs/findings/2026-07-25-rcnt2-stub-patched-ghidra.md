# RCnt2 FORCE stub patched in Ghidra

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [playtest-always-force](2026-07-25-playtest-always-force.md)

## Listing

```
800abb7c  lui at,0x1f80
800abb80  lw  v0,0x1120(at)     ; RCnt2
800abb84  nop
… lure compare → sh g_danger …
800abbd4  jal increment_step_id ; intact
800abbd8  nop
```

## Next

Export → compress → CDmage pad-Yes → DuckStation (expect sparse FORCE, not every check).
