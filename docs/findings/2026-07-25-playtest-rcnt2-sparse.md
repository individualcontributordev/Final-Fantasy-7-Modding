# Playtest: RCnt2 stub — sparse encounters

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [playtest-always-force](2026-07-25-playtest-always-force.md), [export-stale-mfc0](2026-07-25-export-stale-mfc0.md)

## Build

- `xxd @ 0xBB7C`: `80 1f 01 3c 20 11 22 8c` (RCnt2 stub)  
- Compress: `FIELD.BIN.new` 85358 (−77)

## Encounter samples (StepID / Offset)

| StepID | Offset |
|--------|--------|
| 46 | 0 |
| 94 | 0 |
| 122 | 0 |
| 128 | 0 |
| 148 | 0 |
| 200 | 0 |
| 8 | 13 |
| 12 | 13 |
| 22 | 13 |

Not every StepID+2. Offset **0→13** after StepID wrap matches vanilla tape advance (boss preempt routing preserved at mechanism level).

## Follow-ups

- [x] Lure scaling via RAM poke (1/16/64)  
- [ ] Optional FORCE rate tune (`lure` vs `lure>>n`)  
- [ ] Scripted preempt boss smoke (Aps etc.)
