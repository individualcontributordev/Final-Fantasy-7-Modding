# FUN_800a14d8 uses scratchpad, not root counters

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [entropy-1f80-hits](2026-07-25-entropy-1f80-hits.md)

## Summary

`FUN_800a14d8` writes `0x1F800000/004/008` — PS1 **scratchpad** temps for camera/entity distance math, **not** RCnt at `0x1F8011xx`.

## Entropy decision

Vanilla FIELD need not already use a timer. Our in-place stub can **introduce**:

```text
mfc0  <reg>, Count    ; COP0 Count — free-running
```

Mix with `g_enemy_lure` for FORCE probability. Independent of StepID/Offset.

## Follow-ups

- [ ] Implement stub with `mfc0` + lure-scaled FORCE
- [ ] `g_danger = 0` at `field_map_init` entry
