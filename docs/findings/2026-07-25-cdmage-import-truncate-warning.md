# CDmage truncate warning on FIELD.BIN import

**Date:** 2026-07-25  
**Confidence:** confirmed (UI)  
**Related:** [force-stub-compressed](2026-07-25-force-stub-compressed.md)

## Summary

CDmage: *"Import file is longer than file in the image. Import file will be truncated."*

**Do not Continue** — truncation corrupts the import.

## Why this is unexpected

| File | Size |
|------|------|
| Stock `FIELD.BIN` | 85435 |
| `FIELD.BIN.new` | 85355 (−80) |

A correct replace of engine `FIELD.BIN` with `.new` should **not** say “longer”. Likely causes:

1. Imported `FIELD.BIN.dec.patched` (264008) by mistake, or
2. Replaced a **FIELD folder** map file (`.BSX` / `.DAT`) instead of disc `FIELD.BIN`

Screenshot background showed `FRCYO.BSX` / `FSHIP_*` — map files, not the engine binary.

## Also

Creating a `.cue` for `ff7_disc1_test.bin` so CDmage can open it is normal/fine.
