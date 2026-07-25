# g_enemy_lure labeled @ 0x80062F19

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [danger-add-block-size](2026-07-25-danger-add-block-size.md), [patch-target-field-load-reseed](2026-07-25-patch-target-field-load-reseed.md)

## Summary

`DAT_80062f19` → **`g_enemy_lure`**. Loaded as a **byte** (`lbu`) in the threshold path.

## Evidence

```
800abc1c  lhu a0, g_danger
800abc24  lbu v1, g_enemy_lure    ; 0x80062F19
800abc2c  mult a0, v1
800abc30  andi v0, v0, 0xff       ; roll
800abc34  mflo v1
800abc38  srl  v1, v1, 0xc        ; (Danger * lure) >> 12
```

## MAX Danger note

Need `(Danger * lure) >> 12 ≥ 256` to always beat the roll.  
With `Danger = 0xFFFF`: requires **`lure ≥ 16`**. If lure can be lower, `0xFFFF` alone is not enough — force the battle branch or clamp lure in the stub.

## Follow-ups

- [ ] Xrefs to `g_enemy_lure` (who writes default / materia)
- [ ] Entropy source + assemble in-place stub
