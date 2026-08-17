# Single-Disc Architecture: Final Understanding [RESOLVED]

**Date:** 2026-08-17
**Context:** v0.1.39 regression - missing DSKCG removals and CSR field changes
**Status:** ✅ FULLY CLARIFIED - Correct architecture documented

**⚠️ CRITICAL RULE: NEVER MODIFY CSR LAYERS - They are correct as-is!**

All changes are to `builder/single-disc-on-csr/layers/disc1.layer.json` ONLY.

## The Critical Insight

User's clarification: **The same field may be edited in disc 1 and disc 2 for different parts of the game**

Example: Field `BLACKBGB` is edited differently on D1 vs D2 because:
- D1 version: Used when the player first visits during Disc 1 gameplay
- D2 version: Used when the player visits the same location during Disc 2 gameplay

**This means you CANNOT just apply CSR D1 layer and call it done!**

## Correct Architecture

### 1. CSR Multi-Disc Field Edits
From `docs/findings/2026-08-06-csr-multi-disc-field-edits.md`:
- 174 fields edited on D1
- 71 fields edited on D2
- 4 fields edited on D3
- **10 fields edited on BOTH D1 and D2** with different content for different game moments

### 2. Field Merge Policy
From `mods/single-disc/patches/csr-field-disc-prefer.txt` - the prefer list:
- **prefer-D1**: Keep CSR D1 version (e.g., `BLACKBGB`, `DEL1`, `LOSIN2`)
- **prefer-D2**: Use CSR D2 version (e.g., `LOST2`, `CANON_2`)
- **review**: Manual Makou comparison required (7 fields need human review)

### 3. DSKCG Removals (19 operations)
From `docs/findings/2026-08-02-single-disc-ask-for-disc-inventory.md`:
- Field 103 (`BLACKBGB`): 4 asks
- Field 106 (`BLACKBGE`): 1 ask
- Field 95 (`BLACKBG3`): 14 asks

### 4. LOST2 IFUW Music Patch
From v0.1.39 layer (already exists):
- 16,726 records patching decompressed LOST2 script
- Forces break scene music when GM != 0xa455

### 5. SNOVA Inject
From `inject_snova_d3_to_d1.py`:
- Copy SNOVA files from pristine D3 to D1
- Patch BATTLE.X LBA entries

## Correct Workflow (REVISED)

The workflow is NOT "apply CSR D1 and done" - it's a smart merge:

1. **Start with pristine D1**
2. **Apply CSR D1 layer** (gets 174 CSR D1 field edits)
3. **Selectively apply CSR D2 layer fields** following the prefer list:
   - From `csr-d2d3-field-merge-on-d1.md`: 77 files from D2/D3
   - From `csr-field-disc-prefer.txt`: Use prefer-D2 policy for conflicts
   - Example: Keep `BLACKBGB` from D1, replace `LOST2` with D2 version
4. **Remove 19 DSKCG operations** via Makou Reactor
5. **Apply LOST2 IFUW patch** (already in v0.1.39 layer - merge it)
6. **Inject SNOVA** from pristine D3
7. **Diff against pristine D1** to create the layer

## Why This Is Complex

The 77 files from `csr-d2d3-field-merge-on-d1.md` are CSR D2/D3 field edits that need to be on the single Disc 1 image.

**BUT**: 10 of those files have DIFFERENT edits on D1 vs D2, so you can't just blindly overwrite D1 with D2.

The prefer list tells you which version to use for each conflict:
- `DEL1.DAT`: CSR D1 removes MAPJUMP to field 442; D2 keeps it → **prefer-D1**
- `LOST2.DAT`: D2 has the break scene logic → **prefer-D2**
- `BLACKBGB.DAT`: D1 hub/routing; Ask-stripped → **prefer-D1**

## Expected Layer Size

The v0.1.40 layer should be **~850k+ records**:
- CSR D1 field changes (~174 files)
- CSR D2/D3 field changes merged in (~77 files, respecting prefer list)
- DSKCG removals (19 operations across 3 fields)
- LOST2 IFUW patch (16,726 records)
- SNOVA inject (final battle files + BATTLE.X LBA patches)

All changes diffed against pristine D1 to create the layer.

## Implementation Approach

The existing script `build_csrplus_and_highwind_d1_layers.py` shows the pattern:

1. Create baseline: pristine + CSR D1 + existing single-disc layer
2. Inject specific CSR+ D2/D3 fields from source images
3. Diff against pristine to create new layer

For v0.1.40, we need a similar approach but manually merging the 77 D2/D3 files according to the prefer list.

## Updated Documentation Status

`docs/INSTRUCTIONS.md` needs to be COMPLETELY REWRITTEN with the correct merge workflow.

The current version incorrectly states "just apply CSR D1 layer" - this will lose critical D2/D3 field changes that are needed for late-game content.
