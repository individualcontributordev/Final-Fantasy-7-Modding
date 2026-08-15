# CSR × Single-Disc Layer Conflict Analysis

**Date:** 2026-08-15  
**Status:** Investigation complete — found root cause of CSR breakage

## Summary

Analyzed overlapping byte patches between CSR base layers and the single-disc mod to understand why single-disc breaks CSR when stacked. Found that the single-disc layer was **built from CSR, not pristine**, so most overlaps are intentional and safe. However, **926 CSR Disc 1 edits are being overwritten** by single-disc with different bytes.

---

## Layer Sizes

| Layer | Records | Offset Range | Notes |
|-------|---------|--------------|-------|
| CSR Disc 1 | 94,148 | LBA 614 to 126,073 | Field/movie/system edits |
| CSR Disc 2 | 36,524 | LBA 614 to 126,373 | Field/movie edits |
| CSR Disc 3 | 2,924 | LBA 614 to 125,458 | Minimal field edits |
| Single-disc | 834,218 | LBA 17,699 to 343,941 | D2+D3 data relocated to D1 |

**Single-disc breakdown:**
- 0-100 MB (SYSTEM): 588 records
- 100-200 MB (FIELD): 13,499 records
- 200-300 MB (DATA): 11,835 records
- **400+ MB (APPENDED):** 808,296 records — **D2/D3 movies relocated to end of D1**

Max LBA: **343,941** = MSF **76:25:66** (fits on 80-minute CD-R)

---

## Overlap Analysis

### CSR D1 ∩ Single-disc: **926 offsets**

- **Same bytes:** 0 (0%)
- **Different bytes:** 926 (100%)

**All 926 overlaps write different bytes!**

These are in:
- FIELD range (30k-60k LBA): 135 offsets
- DATA1 range (60k-100k LBA): 279 offsets
- DATA2 range (100k-130k LBA): 512 offsets

### CSR D2 ∩ Single-disc: **15,154 offsets**

- **Same bytes:** 14,498 (95%)
- **Different bytes:** 656 (4%)

**95% of overlaps are identical bytes!** This proves single-disc was built **from CSR D2**, not pristine. The layer is correctly preserving CSR's Disc 2 field edits when relocating them to Disc 1.

---

## Root Cause of CSR Breakage

### Problem

The **926 CSR Disc 1 conflicts** are the issue. Single-disc overwrites CSR D1 edits with different bytes at 926 offsets.

**Hypothesis:** Single-disc was built against:
- ✅ CSR Disc 2 (95% byte match proves this)
- ❌ **Pristine Disc 1** (0% byte match with CSR D1 suggests this)

When applied in order `CSR D1 → Single-disc D1`, the single-disc layer **undoes** 926 of CSR's Disc 1 field edits.

### Impact

If CSR makes critical field script changes on Disc 1 (e.g., cutscene removal, dialogue edits), and single-disc restores pristine bytes at those same offsets, **CSR changes are lost**.

---

## Solution Options

### Option 1: Rebuild single-disc from CSR D1+D2+D3 (recommended)

The single-disc ship scripts in `mods/single-disc/scripts/` should be updated to:

1. Start from **CSR Disc 1** (not pristine)
2. Apply Ask-for-disc removal on top of CSR's existing field edits
3. Append D2/D3 movies to end of D1
4. Remap SNOVA LBAs
5. Diff against **CSR D1** (not pristine) to build the layer

This ensures single-disc **preserves all CSR D1 edits** while adding single-disc functionality.

### Option 2: Split into two layers

- **single-disc-core:** Ask-for-disc removal + SNOVA patches only (no D2/D3 relocation)
- **single-disc-movies:** D2/D3 movie relocation + movie table patches

Apply order: `CSR D1 → single-disc-core → single-disc-movies`

This lets single-disc-core avoid overwriting CSR D1 by only patching known Ask-for-disc opcodes.

### Option 3: Manual conflict resolution

Keep the current layer but add a **post-patch step** that re-applies the 926 CSR D1 edits on top of single-disc.

Not recommended — fragile and hard to maintain when CSR updates.

---

## Recommended Next Steps

1. **Verify hypothesis:** Check if the ship scripts in `mods/single-disc/scripts/ship_v025b.py` (or latest) actually build from CSR or pristine

2. **If from pristine:** Update ship script to:
   ```python
   # Instead of:
   pristine_d1 = load("pristine/FINALFANTASY7_D1.bin")
   
   # Use:
   csr_d1 = apply_layer(
       load("pristine/FINALFANTASY7_D1.bin"),
       load("Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json")
   )
   ```

3. **Rebuild layers** with corrected baseline

4. **Test** that CSR + single-disc preserves CSR field edits

---

## Related

- **Ship scripts:** `mods/single-disc/scripts/ship_v025b.py`
- **CSR layers:** `Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/`
- **Layer format:** `ic-layer-v1` (offset + hex records)
- **Builder logic:** `individualcontributordev.github.io/builder/layer.js`

