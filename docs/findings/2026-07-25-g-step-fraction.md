# g_step_fraction renamed via lbu xref

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [encounter-check-renamed](2026-07-25-encounter-check-renamed.md)

## Summary

Step fraction labeled **`g_step_fraction`** via `lbu`/`sb` at `0x800ABAB4` / `0x800ABAC4` (RAM `0x8009C6D8`).

## Evidence

```
800abab4  lbu v0,-0x3928(v0)=>g_step_fraction
800ababc  addiu v0,v0,0x20
800abac4  sb  v0,-0x3928(at)=>g_step_fraction
```

Matches wiki: step fraction += 32 each check tick.
