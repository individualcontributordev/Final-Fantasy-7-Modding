# FORCE stub patched; jal at ABBD4 clobbered

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [danger-max-stub-draft](2026-07-25-danger-max-stub-draft.md)

## Summary

In-place FORCE stub at `0x800ABB7C`–`0x800ABBD0` matches assembled bytes. Selection overran: `0x800ABBD4` is `nop` instead of `jal increment_step_id`. Delay `nop` @ `0x800ABBD8` and following `lui`/`lbu` @ `0x800ABBDC` look intact.

## Verified stub Listing

```
800abb7c  mfc0 v0,Count
800abb80  lui at,0x8006
800abb84  lbu v1,0x2f19(at)
800abb88  andi v0,v0,0xff
800abb8c  sltu v0,v0,v1
800abb90  subu v0,zero,v0
800abb94  lui at,0x8007
800abb98  sh v0,0x173c(at)
800abb9c–800abbd0  nop ×14
800abbd4  nop          ← MUST restore jal increment_step_id
800abbd8  nop          ← OK (delay slot)
800abbdc  lui v1,0x8006
800abbe0  lbu DAT_80062f1b
```

## Restore

| VA | Bytes (LE) | Asm |
|----|------------|-----|
| `0x800ABBD4` | `72 ae 02 0c` | `jal increment_step_id` (`0x800AB9C8`) |
