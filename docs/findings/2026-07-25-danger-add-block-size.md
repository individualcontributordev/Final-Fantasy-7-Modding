# Danger += block sized for in-place patch

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [patch-target-field-load-reseed](2026-07-25-patch-target-field-load-reseed.md), [danger-increment](2026-07-25-danger-increment.md)

## Summary

Vanilla Danger growth is **`0x800ABB7C`–`0x800ABBD4`** (exclusive end) = **`0x58` (88) bytes**, 22 MIPS instructions. Fits an in-place MAX-RNG stub; then fall through to `jal increment_step_id` @ `0x800ABBD4`.

## Listing (patch region)

```
800abb7c  lui / addiu / addu / lhu   ; scale table
800abb8c  srl a0,8
800abb90  div + div-by-zero breaks
800abbb8  mflo v1
800abbbc  lhu g_danger / addu / sh g_danger
800abbd4  jal increment_step_id       ; KEEP — not overwritten
```

## Follow-ups

- [ ] Label `DAT_80062f19` → `g_enemy_lure`
- [ ] Choose entropy (e.g. COP0 Count / root counter)
- [ ] Assemble in-place stub + `g_danger=0` in `field_map_init`
