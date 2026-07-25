# CDmage: wrong FIELD.BIN (inside FIELD/ folder)

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [cdmage-import-truncate-warning](2026-07-25-cdmage-import-truncate-warning.md)

## Summary

Truncate warning persists because import targeted **`FIELD/FIELD.BIN`** (map-folder file), not the **disc-root engine** `FIELD.BIN`.

## Evidence

- `ls`: `FIELD.BIN.new` = 85355, stock extract = 85435 (correct engine sizes)
- CDmage: `FIELD` folder selected; `FIELD.BIN` highlighted among `.DAT`/`.BSX` map files
- Same truncate dialog → that in-folder `FIELD.BIN` is **smaller** than our `.new`

## Correct target

ISO root (Track 1), sibling of folders `FIELD`, `BATTLE`, `WORLD`, … — file named **`FIELD.BIN`**.

Do **not** import into anything under the `FIELD/` directory.
