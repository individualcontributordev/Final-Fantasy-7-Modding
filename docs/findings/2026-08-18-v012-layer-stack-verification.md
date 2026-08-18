# v0.1.2 Layer Stack Verification - Complete Investigation

**Date:** 2026-08-18  
**Issue:** Rebuilt v0.1.2 bin fails disc 1→2 transition (no "save game?" prompt)  
**Root Cause:** Published layers missing data + incorrect EDC/ECC

## Summary

The working v0.1.2 bin is **CSR v0.14.1 + single-disc (fields + movies + endings) + EDC/ECC**.

When extracted correctly from CSR base, the complete single-disc layer produces a **byte-for-byte perfect match** to the working bin.

## Investigation Process

### Attempt 1: Extract from Pristine ❌
- Diffed: working bin vs pristine
- Result: 4.2M records (742MB) - includes CSR changes
- Problem: Includes CSR base data, not just single-disc changes

### Attempt 2: EDC/ECC Repair ❌
- Implemented Python PSX Mode 2 Form 1 EDC/ECC
- Applied published layers + EDC/ECC repair
- Result: Still 1% different (1,121 data sectors wrong, 22,084 EDC/ECC sectors wrong)
- Problem: Python EDC/ECC doesn't match builder's edc.js, and layers missing data

### Attempt 3: Extract from CSR Base ✅
- Built CSR v0.14.1 D1 base (pristine + CSR layers)
- Diffed: working bin vs CSR base
- Result: 4.1M records (735MB) - PERFECT MATCH when re-applied

## Layer Breakdown

**Complete single-disc layer (extracted from CSR base):**
- Records: 4,146,641
- Changed bytes: 251,540,010
- JSON size: ~735 MB
- Contents: Field changes + manip-movies + endings + EDC/ECC

**Published layers (current broken setup):**
1. Field layer: 96,497 records (3.9 MB)
2. Manip-movies: 841,849 records
3. Endings 1-7: 3,271,021 records (combined)
4. **Total: 4,209,367 records** (more than extracted!)

**Difference:** 62,726 more records in published vs extracted (?)

## Binary Comparison: Published vs Working

**When applying published layers (field + manip + endings) to CSR base:**
- Size: ✅ 766,340,400 bytes (matches working)
- Data differences: ❌ 1,121 sectors
- EDC/ECC differences: ❌ 22,084 sectors
- Total: ❌ 8,049,388 bytes different (1.05%)

**Sector analysis:**
- 5 sectors in ISO filesystem metadata (< sector 500)
- Rest scattered across movies/endings regions
- Suggests ISO generation + content differences

## Conclusion

The extracted single-disc layer from CSR base is **correct**. It produces an exact match to the working bin.

The published layers are **incorrect** - they have:
1. Wrong data in 1,121 sectors
2. Wrong or missing EDC/ECC in 22,084 sectors

## Next Steps

**Option A: Publish Complete Layer (735MB)**
- Single massive layer with everything
- Browser may struggle with 735MB JSON download
- Simple but possibly too large

**Option B: Split Correctly**
- Extract field-only layer from working bin
- Use published manip-movies + endings (if they're correct)
- Add EDC/ECC corrections if needed

**Option C: Use Builder's EDC/ECC**
- Publish data-only layers (no EDC/ECC)
- Let builder calculate EDC/ECC automatically
- Need to verify builder does this

## Files Created

- `workspace/csr-v0.14.1-d1-base.bin` - CSR v0.14.1 D1 base
- `workspace/v012-single-disc-only-from-csr-base.json` - Complete correct layer (735MB)
- `workspace/v012-extracted-complete-layer.json` - From pristine (wrong - has CSR)
- `workspace/v012-missing-data-layer.json` - Difference between published and working
- `scripts/edc_ecc.py` - Python EDC/ECC (doesn't match builder)
- `mods/single-disc/scripts/build_v012_with_edc.py` - Local build attempt
