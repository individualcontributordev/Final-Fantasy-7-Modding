# No root-counter / mfc0 entropy in FIELD.BIN

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [patch-target-field-load-reseed](2026-07-25-patch-target-field-load-reseed.md)

## Summary

Searches in FIELD.BIN Ghidra project:

| Query | Result |
|-------|--------|
| Scalar `0x1f801110` | none |
| Scalar `0x1f801120` | none |
| Instruction `mfc0` | none |

FIELD does not directly reference those PS1 root counters / COP0 Count in a way Ghidra finds.

## Entropy options (fallback order)

1. Broader IO: scalar **`0x1f80`** (`lui` to IO segment) — any RCnt/GPU/timer use
2. Existing VSync/BIOS helpers already called from FIELD (e.g. `SUB_80043dd8`) — find a frame counter they update
3. **Mix non-StepID state** each encounter check: e.g. `g_step_fraction`, Cloud X/Y, `g_formation`, `g_enemy_lure` — not the StepID tape; still somewhat manipulable but breaks pure table routing
4. DuckStation: identify a RAM byte that increments while standing still → hardcode that address

## Follow-ups

- [ ] Search scalar `0x1f80`
- [ ] Pick final entropy and draft stub
