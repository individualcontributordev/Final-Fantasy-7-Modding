# No-swap — Makou Ask-for-disc removal playtest (pristine D1)

**Date:** 2026-08-03
**Confidence:** confirmed on DuckStation; **console not tested**
**Method:** Delete all field **Ask for disc** (DSKCG) ops in Makou on pristine D1
working image; leave Set next movie / Play movie; vanilla FIELD.BIN (no engine stubs).

## Result

| Check | Result |
|-------|--------|
| DuckStation disc-change / no insert-disc path | **PASS** |
| Console (PS1/PS2/burn) | **Not tested** |

Operator report: playtest for removing disc asks passed on DuckStation; console not tested.

## Context

- Engine MOVIE/DSKCG entry stubs abandoned earlier (intro softlock / black disc-change).
- Playable path is Makou DSKCG removal only for Ask gates.
- FMV: leave Play movie (wrong D2/D3 FMV on D1 acceptable for clean).
- CSR later: optional copy of manip-critical movies onto D1; CSR+/Highwind need no movie copy.
- Supernova (`SNOVA/` D3-only) still open if final battle on D1-only.

## Next

1. Keep work bin for diff when ready to pack (after more full-run gates).
2. Supernova: copy `SNOVA/` D3→D1 or battle stub.
3. Console smoke when convenient (not blocking further RE).
4. Ship pack only after full-run policy gates (Ask PASS is necessary but not sufficient alone if Supernova/endings still freeze).
