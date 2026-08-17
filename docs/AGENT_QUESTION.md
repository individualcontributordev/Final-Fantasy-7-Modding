# Agent Clarification Needed: Single-Disc v0.1.40 Rebuild

**Date:** 2026-08-17  
**Context:** v0.1.39 regression - missing DSKCG removals and CSR field merges  

## Current Understanding

Based on user feedback and repository documentation, the single-disc mod requires:

### 1. CSR D1+D2+D3 Field Merge (77 files)
From `mods/single-disc/patches/csr-d2d3-field-merge-on-d1.md`:
- 72 files from CSR D2 FIELD changes
- 5 files from CSR D3 FIELD changes  
- These must be merged onto D1 to preserve CSR story fixes across all discs

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
- Copy SNOVA files from D3 to D1
- Patch BATTLE.X LBA entries

### 5. Ending Movies (7 auto layers)
From ending-credits layers:
- Copy D3 ending movies to D1 freed movie slots

### 6. CSR Manip-Movies (optional separate pack)
From `csr-manip-movie-whitelist.md`:
- Copy required CSR D2/D3 movies to D1
- Not part of core single-disc layer

## Question for User

**What is the correct base for building the single-disc layer?**

### Option A: CSR bases (agent's new understanding)
Start with CSR D1 (from Final-Fantasy-7-CSR repo), then:
1. Merge CSR D2/D3 field changes (via script or Makou)
2. Remove DSKCG operations (Makou Reactor)
3. Apply LOST2 patch
4. Inject SNOVA
5. Build layer by diffing against **CSR D1** (not pristine)

### Option B: Pristine base (original INSTRUCTIONS.md)
Start with pristine D1, then:
1. Remove DSKCG operations (Makou Reactor)
2. Apply LOST2 patch (manual or script)
3. Inject SNOVA
4. Build layer by diffing against **pristine D1**
5. CSR changes applied separately by the browser builder layering

## Existing Scripts

The repo has `build_csrplus_and_highwind_d1_layers.py` which:
- Loads CSR D1 as baseline
- Applies existing single-disc layer
- Merges CSR+ scene pack fields from D2/D3
- Diffs against pristine to create new layer

But this script expects an existing single-disc layer to start with.

## Agent's Hypothesis

The correct workflow is probably:

1. **Start with CSR D1+D2+D3 bins** (built from Final-Fantasy-7-CSR)
2. **Manually merge D2/D3 FIELD files onto D1** (77 files via Makou or script)
3. **Remove 19 DSKCG operations** (Makou Reactor)
4. **Apply LOST2 IFUW patch** (script ship_v037.py generates this)
5. **Inject SNOVA** (inject_snova_d3_to_d1.py)
6. **Diff merged D1 against pristine D1** to create layer
7. **Layer contains all changes**: CSR D1+D2+D3 fields + DSKCG removals + LOST2 + SNOVA

This would explain why the layer should have ~850k records (full CSR field merges + patches).

## Request

Please confirm which approach is correct, and I'll update INSTRUCTIONS.md with the proper workflow.

If Option A is correct, I need to know:
- How to merge CSR D2/D3 FIELD files onto CSR D1 (Makou manual? Script exists?)
- Whether to use `build_csrplus_and_highwind_d1_layers.py` or a different script
- Whether ship_v037.py LOST2 patch is still the right approach

If Option B is correct, the current INSTRUCTIONS.md is mostly right, but missing the understanding that CSR changes are applied by the builder, not baked into the layer.
