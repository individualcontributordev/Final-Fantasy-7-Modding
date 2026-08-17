# Finding: Working v0.1.2 Single-Disc Analysis

**Date:** 2026-08-17  
**Source:** `/Users/david.morton/Downloads/ff7-d1-csr-sd-mov-end.bin`  
**Size:** 766,340,400 bytes  
**Status:** ✅ Complete and working (except ending movie audio flicker)

## Summary

Analyzed the working v0.1.2 single-disc bin to understand correct build pattern for v0.1.40.

## Key Findings

### Field Source Preferences

| Field | Source | Notes |
|-------|--------|-------|
| LOST2 | CSR D2 | ✅ Exact match - includes break scene (MAPJUMP to cos_btm2) |
| DEL1 | CSR D1 | ✅ Exact match |
| LOSIN2 | CSR D1 | ✅ Exact match |
| CANON_2 | CSR D2 | ✅ Exact match |
| BLACKBGB | Custom | DSKCG removed (13,013 bytes, same as CSR D1/D2) |
| BLACKBGE | Custom | DSKCG removed (7,405 bytes, all sources identical) |
| BLACKBG3 | Custom | DSKCG removed (22,203 bytes, all sources identical) |

### DSKCG Removal Status

**✅ All 19 DSKCG operations removed:**
- BLACKBGB: 0 DSKCG (was 4)
- BLACKBGE: 0 DSKCG (was 1)
- BLACKBG3: 0 DSKCG (was 14)

### LOST2 Break Scene

**CSR D2 LOST2 `init / Slot 0, opcode position 10`:**
```
IFUW bytes: 1820000055a4000b
Else-jump: 0xA4
Next op: MAPJUMP to field 526 (0x020E) = cos_btm2
```

**Status:** ✅ Working on single-disc!

The documentation mentioned changing else-jump from 0x0B → 0x00, but the working bin has 0xA4. This means **CSR D2 LOST2 already works for single-disc** - just use it as-is.

## Movie Issues (Reported by User)

1. **Ending movie:** Audio flickering
2. **Field 637, id 2, script 0, line 54:** Movie has flickering

These are the only known issues in v0.1.2.

## Build Pattern for v0.1.40

### Step 1: Start with Pristine D1

```
workspace/pristine/FINALFANTASY7_D1.bin
```

### Step 2: Apply CSR D1 Layer

```python
# Load CSR D1 layer (174 field edits from CSR repo)
csr_d1_layer = load_layer("Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json")
apply_layer(work_bin, csr_d1_layer)
```

### Step 3: Merge CSR D2/D3 Fields

Following the prefer policy from `csr-field-disc-prefer.txt` and `csr-d2d3-field-merge-on-d1.md`:

**Prefer D2 (use CSR D2 version):**
- LOST2 (break scene!)
- CANON_2
- Any others marked prefer-D2 in the policy

**Prefer D1 (keep CSR D1 version):**
- DEL1
- LOSIN2
- BLACKBGB (but need to remove DSKCG)
- Any others marked prefer-D1

### Step 4: Remove DSKCG from 3 Fields

Use Makou Reactor to delete 19 "Ask for disc" operations:
- BLACKBGB init/Slot 0: 4 DSKCG
- BLACKBGE AD/Slot 4: 1 DSKCG  
- BLACKBG3 p7/Slot 1: 1 DSKCG, p8/Slot 1: 13 DSKCG

### Step 5: Inject SNOVA from Pristine D3

Move Disc 3 final battle files to Disc 1, patch BATTLE.X LBAs.

### Step 6: Build Layer

Diff against pristine D1 to create `disc1.layer.json`.

## Critical Requirements

1. ✅ **LOST2 must be CSR D2** for break scene to work
2. ✅ **All 19 DSKCG removed** for no disc swap prompts
3. ✅ **SNOVA injected** for final battle on Disc 1
4. ⚠️ **Movie audio flicker** needs investigation (low priority - playable)

## Console Compatibility

v0.1.2 confirmed working on console hardware (burns to disc, plays on PSX/PS2).

## Next Steps

1. Update `build_v0140.py` with CSR D2 LOST2 preference
2. Build v0.1.40 layer
3. Test disc 1→2 transition (should have break scene)
4. Investigate movie audio flicker (separate issue)
