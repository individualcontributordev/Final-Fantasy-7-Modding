# FIELD.BIN.new compressed successfully

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [force-stub-export-verified](2026-07-25-force-stub-export-verified.md)

## Summary

Patched `.dec` recompressed; output **smaller** than stock (−80 bytes) → safe in-place ISO replace.

| File | Size |
|------|------|
| `FIELD.BIN` (stock) | 85435 |
| `FIELD.BIN.new` | 85355 |
| `FIELD.BIN.dec.patched` | 264008 |

## Next

Import `FIELD.BIN.new` into `ff7_disc1_test.bin` → DuckStation smoke test.
