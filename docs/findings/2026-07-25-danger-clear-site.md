# Danger clear at 0x800A1C70 is post-battle cleanup (caller of FUN_800a1368)

**Date:** 2026-07-25  
**Confidence:** likely  
**Related:** [g-danger-xrefs](2026-07-25-g-danger-xrefs.md)

## Summary

`sh zero → g_danger` at `0x800A1C70` is **not** inside `FUN_800a1368`. That function is only `jal`'d from `0x800A1C20`. The clear is in the **caller** (Ghidra xref: `FUN_800a16cc`).

## Evidence

Around the clear:

```
800a1c20  jal FUN_800a1368
800a1c28  ...
800a1c3c  bne (DAT_800965ec != 2) → skip
800a1c48  lbu DAT_8007ebc8
800a1c54  bne != s2 → skip
800a1c60  sb zero → DAT_8007ebc8
800a1c68  sb zero → g_step_fraction
800a1c70  sh zero → g_danger
800a1c74  sb zero → DAT_8009abf5
```

Matches battle teardown: `encounter_check` sets `DAT_8007ebc8 = 1` and `DAT_8009abf5 = 2` when starting a fight; this block clears those plus Danger / step fraction.

## Implications

- This is almost certainly **after battle**, not field enter.
- Field-enter `Danger = 0` still needs its **own** hook.

## Follow-ups

- [ ] Confirm function start `FUN_800a16cc` @ `0x800A16CC` and label (e.g. `after_battle_cleanup`)
- [ ] Find field map enter / init for Danger = 0 hook
