# CDmage: Cannot write ff7_disc1_test.bin

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [cdmage-save-options-pending](2026-07-25-cdmage-save-options-pending.md)

## Summary

Save failed: `Cannot write to file: ...\ff7_disc1_test.bin`.

Import may be in memory only until a successful save.

## Likely causes

1. DuckStation (or another app) has the `.bin`/`.cue` open  
2. File marked read-only  
3. Second CDmage instance / explorer preview lock  

## Fix order

1. Close DuckStation completely  
2. Clear read-only on `ff7_disc1_test.bin`  
3. Retry Save (OK on Save options)  
4. If still fails: **Save As** `ff7_disc1_test_patched.bin` + matching `.cue`
