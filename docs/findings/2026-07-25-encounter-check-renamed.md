# encounter_check renamed at 0x800ABA70

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [encounter-check-entry](2026-07-25-encounter-check-entry.md)

## Summary

`FUN_800aba70` renamed to **`encounter_check`** at `0x800ABA70`.

## Evidence

```
encounter_check  XREF[1]: FUN_800a65a4:800a6ec0(c)
800aba70  lui v0,0x800a
800aba78  addiu sp,sp,-0x28
800aba7c  sw ra / s2 / s1 / s0
```

## Follow-ups

- [ ] Rename `DAT_8009c6d8` → `g_step_fraction` (via code xref; RAM outside FIELD map)
- [ ] Label `FUN_800aba34` / caller `FUN_800a65a4`
