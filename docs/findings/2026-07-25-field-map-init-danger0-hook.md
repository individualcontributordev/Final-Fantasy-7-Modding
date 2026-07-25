# field_map_init entry — Danger=0 hook site

**Date:** 2026-07-25  
**Confidence:** likely  
**Related:** [field-map-init-renamed](2026-07-25-field-map-init-renamed.md), [patch-target-field-load-reseed](2026-07-25-patch-target-field-load-reseed.md)

## Summary

`field_map_init` @ `0x800BA534` prologue already clears several bytes. **In-place Danger=0:** replace the `DAT_8009fe8c = 0` pair with `g_danger = 0` (same 2 instructions).

## Entry (relevant)

```
800ba534  addiu sp / sw s0 / move s0,a2 / sw ra
800ba544  lh v0,0x6a(a0)
800ba548  ori v1,1
… pointer stores …
800ba568  sb zero → DAT_80095dcc
800ba570  sb 1    → DAT_8007ebe0
800ba574  lui at,0x800a
800ba578  sb zero → DAT_8009fe8c    ← REPLACE with g_danger clear
```

## Proposed replacement (2 ins)

```
lui  at, 0x8007
sh   zero, 0x173c(at)    ; g_danger @ 0x8007173C
```

## Follow-ups

- [ ] Xrefs to `DAT_8009fe8c` — confirm safe to drop that clear
- [ ] Assemble Danger+= stub (`mfc0` + lure-scaled FORCE)
