# Agent Understanding: Single-Disc v0.1.40 Rebuild [RESOLVED]

**Date:** 2026-08-17
**Context:** v0.1.39 regression - missing DSKCG removals and CSR field changes
**Status:** ✅ CLARIFIED - User confirmed the architecture

## Confirmed Understanding

User clarified: **FF7 D1/D2/D3 share the same code - only movies differ.**

The single-disc mod workflow is:

### 1. CSR D1 Layer (contains all CSR story fixes)
- CSR D1/D2/D3 layers all contain the same field/code changes
- The browser builder applies CSR D1 layer to pristine D1
- Single-disc layer stacks on top

### 2. DSKCG Removals (19 operations)
From `docs/findings/2026-08-02-single-disc-ask-for-disc-inventory.md`:
- Field 103 (`BLACKBGB`): 4 asks
- Field 106 (`BLACKBGE`): 1 ask
- Field 95 (`BLACKBG3`): 14 asks

### 3. LOST2 IFUW Music Patch
From v0.1.39 layer (already exists):
- 16,726 records patching decompressed LOST2 script
- Forces break scene music when GM != 0xa455

### 4. SNOVA Inject
From `inject_snova_d3_to_d1.py`:
- Copy SNOVA files from pristine D3 to D1
- Patch BATTLE.X LBA entries

## Confirmed Workflow

User confirmed the correct approach:

1. **Start with pristine D1**
2. **Apply CSR D1 layer** (contains all CSR story fixes - D1/D2/D3 are the same code)
3. **Remove 19 DSKCG operations** (Makou Reactor)
4. **Apply LOST2 IFUW patch** (already exists in v0.1.39 layer - merge it in)
5. **Inject SNOVA** (from pristine D3)
6. **Diff against pristine D1** to create layer
7. **Layer contains**: All CSR changes + DSKCG removals + LOST2 + SNOVA

The key insight: CSR D1/D2/D3 layers share the same field/code changes. Only movies differ between discs.

The single-disc layer should be ~850k+ records because it contains:
- All CSR D1 field changes (from applying CSR layer before editing)
- DSKCG removals
- LOST2 patch
- SNOVA inject

## Updated Documentation

See `docs/INSTRUCTIONS.md` for the complete v0.1.40 rebuild workflow.

## Notes on Repository Documentation

The `mods/single-disc/patches/csr-d2d3-field-merge-on-d1.md` file listing 77 files is **historical reference** showing which files CSR modified across D2/D3. These changes are already in the CSR D1 layer - no manual merging needed.

The single-disc layer just needs to preserve all CSR changes (by starting with CSR D1 applied) and add the single-disc specific patches (DSKCG removals, LOST2, SNOVA).
