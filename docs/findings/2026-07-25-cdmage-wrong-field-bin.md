# CDmage: wrong FIELD.BIN (inside FIELD/ folder)

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [cdmage-import-truncate-warning](2026-07-25-cdmage-import-truncate-warning.md)

## Summary

Earlier guess that root held engine `FIELD.BIN` was **wrong** — see [cdmage-field-bin-path](2026-07-25-cdmage-field-bin-path.md). Root has only `SCUS_941.63` + `SYSTEM.CNF`.

## Evidence

- `ls`: `FIELD.BIN.new` = 85355, stock extract = 85435 (correct engine sizes)
- CDmage: `FIELD` folder selected; `FIELD.BIN` highlighted among `.DAT`/`.BSX` map files
- Same truncate dialog → that in-folder `FIELD.BIN` is **smaller** than our `.new`

## Correction

Target **is** `FIELD/FIELD.BIN`. Truncate ⇒ restore pristine test ISO, then retry import.
