# Map-setup Danger=0 candidates @ LAB_800a1dc8

**Date:** 2026-07-25  
**Confidence:** likely  
**Related:** [field-map-setup](2026-07-25-field-map-setup.md), [field-map-init-danger0-hook](2026-07-25-field-map-init-danger0-hook.md)

## Summary

`LAB_800a1dc8` already has `lui at,0x8007` + `sh zero` pairs. **Best Danger=0 patch:** retarget one store offset to `g_danger` (`0x173c`) — single-instruction change.

## Listing (relevant)

```
800a1e1c  lui  at,0x8007
800a1e20  sh   zero, DAT_80071e38(at)   ← candidate A
800a1e24  lui  at,0x8007
800a1e28  sh   zero, DAT_80071e3c(at)   ← candidate B
800a1e40  jal  field_map_init
```

## Proposed patch (pick A or B after xrefs)

```
; same lui at,0x8007
sh  zero, 0x173c(at)    ; g_danger @ 0x8007173C
```

## Follow-ups

- [x] Both heavily used — **rejected**; use always-write stub instead
- [ ] Apply + keep FORCE stub as separate patch
