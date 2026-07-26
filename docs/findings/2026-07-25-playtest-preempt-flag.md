# Playtest: preempt flag still 4↔0

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [playtest-rcnt2-sparse](2026-07-25-playtest-rcnt2-sparse.md), [encounter-check](2026-07-25-encounter-check.md)

## Result

`DAT_800716d0` / preempt flag @ `0x800716D0` still goes **4** then resets to **0** while walking. Dual `increment_step_id` preempt path intact under RCnt2 FORCE stub.
