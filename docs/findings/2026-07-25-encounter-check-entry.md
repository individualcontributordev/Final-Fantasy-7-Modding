# encounter_check is FUN_800aba70 @ 0x800ABA70

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [danger-increment](2026-07-25-danger-increment.md), [encounter-check](2026-07-25-encounter-check.md)

## Summary

True entry is **`0x800ABA70`** (`FUN_800aba70`). There is no `jr ra` above the dual `jal`s — Danger add and RNG rolls are mid-function. The old `encounter_check` at `0x800ABBD4` was a bad split inside this function.

## Discovery

Prologue:

```
800aba70  lui / lbu DAT_8009ac30
800aba78  addiu sp,sp,-0x28
800aba7c  sw ra / s2 / s1 / s0
```

Caller xref: `FUN_800a65a4` @ `0x800A6EC0`.

Decompiler (confirmed in one body):

- `DAT_8009c6d8 += 0x20` (step fraction += 32; wraps at 256)
- On wrap: `_g_danger += uVar1 / uVar2` (scale/rate)
- Dual `increment_step_id()` (preempt + threshold)
- Formation via `FUN_800aba34()`
- `s1` set in prologue (fixes prior `unaff_s1`)

## Why no `jr ra`

Scrolling up from `0x800ABB7C` stays inside `FUN_800aba70` until `0x800ABA70`. Do not hunt for `jr ra` mid-function.

## Follow-ups

- [ ] Rename `FUN_800aba70` → `encounter_check`; remove bogus nested fn at `0x800ABBD4` if present
- [ ] Label `DAT_8009c6d8` → `g_step_fraction`
- [ ] Identify caller `FUN_800a65a4` / label `FUN_800aba34`
