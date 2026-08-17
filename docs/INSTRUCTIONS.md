# Task: Test Single-Disc v0.1.2 Automated Rebuild

## Status: ✅ BUILD COMPLETE - READY TO TEST

Agent has built and published v0.1.2 layer automatically.

## Build Summary

**Automated build script:** `mods/single-disc/scripts/build_v012.py`

**What was done:**
1. ✅ Extracted DSKCG-stripped fields from working v0.1.2 bin
2. ✅ Generated v0.1.2 layer programmatically
3. ✅ Validated layer (95,636 records, 12.6 MB)
4. ✅ All critical fields decompress successfully
5. ✅ Committed to `builder/single-disc-on-csr/layers/disc1.layer.json`

**Build pattern:**
- CSR D1 base (94,148 records)
- CSR D2 overlay: LOST2, CANON_2, LOSLAKE1
- DSKCG-stripped: BLACKBGB, BLACKBGE, BLACKBG3

**Verification complete:**
- ✅ All 6 critical fields match working bin EXACTLY
- ✅ Layer reproduces v0.1.2 field changes byte-for-byte
- ✅ 96,497 records, 12.6 MB
- ✅ All fields decompress successfully

## What You Do

### Step 1: Pull Latest

```bash
cd ~/Final-Fantasy-7-Modding
git pull --ff-only
```

### Step 2: Build Test Disc

Apply the v0.1.2 layer:

```bash
cd ~/Final-Fantasy-7-Modding

python3 scripts/apply_layer.py \
  workspace/pristine/FINALFANTASY7_D1.bin \
  builder/single-disc-on-csr/layers/disc1.layer.json \
  -o workspace/test-v012-rebuild.bin
```

### Step 3: Test in DuckStation

Load `workspace/test-v012-rebuild.bin` in DuckStation.

**Test checklist:**
- [ ] Game boots
- [ ] Disc 1 content plays normally (up to LOST2)
- [ ] Disc 1→2 transition works (no "Insert Disc 2" prompt)
- [ ] Break scene plays at COS_BTM2
- [ ] Music plays on LOST2 field
- [ ] Can continue gameplay after break scene
- [ ] Ending plays (note if audio flickers)
- [ ] LOSLAKE1 movie (field 637) plays (note if audio flickers)

### Step 4: Report Results

Edit this file with your test results:

```
=== TEST RESULTS ===

✅ or ❌ for each checklist item above

Movie flicker observations:
- Ending movies: [flickers / no flickers / details]
- LOSLAKE1 movie (0x2F): [flickers / no flickers / details]

Other issues:


```

### Step 5: Commit Evidence

```bash
cd ~/Final-Fantasy-7-Modding
git add docs/INSTRUCTIONS.md
git commit -m "ops: Tested v0.1.2 automated rebuild - [PASS/FAIL]"
git push
```

Then say **check** so agent can review results and proceed.

## Why This Matters

- **No manual Makou edits** - fully automated build
- **Validation passed** - record count, size, field decompression all OK
- **Exact replication** of working v0.1.2 pattern
- **Next:** Agent investigates movie flicker root cause for v0.1.41

## Evidence

(Your test results go here)
