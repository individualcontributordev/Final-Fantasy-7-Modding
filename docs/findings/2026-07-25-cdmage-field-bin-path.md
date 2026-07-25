# Disc layout: engine FIELD.BIN is under FIELD/

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [cdmage-wrong-field-bin](2026-07-25-cdmage-wrong-field-bin.md)

## Summary

Track 1 root of `ff7_disc1_test.cue` has **19 folders + 2 files only**: `SCUS_941.63`, `SYSTEM.CNF`. **No** root `FIELD.BIN`.

Engine module path is **`FIELD/FIELD.BIN`** (prior “wrong folder” call was incorrect about *location*; truncate is still real).

## Truncate still happening

`FIELD.BIN.new` (85355) < stock extract (85435), so a clean image should accept it without “longer… truncated”.

Likely: an earlier **OK** on truncate shrank the image’s `FIELD/FIELD.BIN` slot; `.new` is now longer than the damaged entry.

## Fix

1. Restore test image from pristine  
2. Re-open via `.cue`  
3. Import `FIELD.BIN.new` → `FIELD/FIELD.BIN`  
4. **Cancel** if truncate still appears; note CDmage-reported size of target
