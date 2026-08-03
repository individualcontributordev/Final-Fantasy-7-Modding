# Task: No-swap — Supernova / SNOVA on D1 (after Ask DS PASS)

## Done

- Makou: all **Ask for disc** removed on pristine D1 work bin
- **DuckStation: PASS** (disc asks)
- Console: **not tested**
- Finding: `docs/findings/2026-08-03-noswap-makou-ask-ds-pass.md`

Engine FIELD MOVIE/DSKCG stubs stay abandoned for playable bins.

## Goal this turn

Unblock final battle on D1-only: **Supernova** needs D3 `SNOVA/` (or a battle stub).

Preferred first try (manual / local tools you trust):

1. Keep current Ask-fixed work bin (or copy it):
   `workspace/iso-extract/ff7_d1_noswap_work.bin`
2. From pristine **D3**, copy the entire **`SNOVA/`** tree onto the D1 work image
   (same paths). ~1.1 MB total — smaller than full FMV import.
3. If your ISO tool cannot add files easily: note that under Evidence; we plan
   inject scripts next.
4. DuckStation: reach (or cheat to) final battle / Supernova — must **not** freeze.
5. Confirm new game + disc-change still OK after inject.

## Evidence

```
Work bin path:
SNOVA copy: OK / blocked (why):
Supernova DS: PASS/FAIL/not tested
New game + disc-change still OK: PASS/FAIL/not tested
Console: still untested / notes
```

Say **check**. No pack ship this turn.

## Out of scope

- FIELD MOVIE engine stubs
- CSR manip movie whitelist inject (after Supernova path clear)
- Publishing builder pack
