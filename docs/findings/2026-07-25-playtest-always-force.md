# Playtest: every check FORCEs Danger=65535

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [danger-max-stub-draft](2026-07-25-danger-max-stub-draft.md)

## Result

- Boot / field load: OK  
- Danger on load: 0  
- Every encounter check (StepID += 2): Danger → **65535**, battle, then Danger reset  

## Cause

Stub used `mfc0 v0, Count`. **PSX R3000A has no COP0 Count** (that name is R4000+). Reg 9 is **BDAM**, typically 0 → `(0 < g_enemy_lure)` always true → always FORCE.

## Fix

Replace entropy with **RCnt2** (`lw` from `0x1F801120`), keep lure-scaled branchless store.
