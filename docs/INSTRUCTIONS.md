# Task: Test Single-Disc v0.1.2 Rebuild (Agent Built)

## Context

You tested the manually-built bin at `/Users/david.morton/Downloads/ff7-d1-csr-sd-mov-end.bin` and confirmed it works (disc 1→2 transition, break scene, gameplay complete). The only issues are movie audio flickers (ending + loslake1).

Agent has analyzed the working v0.1.2 pattern and will rebuild it automatically with validation.

## What Agent Will Do

1. ✅ Analyze working v0.1.2 bin (already done)
2. ✅ Write automated build script with validation
3. ✅ Generate v0.1.2 layer (CSR D1 + D2 overlays + DSKCG stripped)
4. ✅ Validate layer (record count, size, decompression)
5. ✅ Commit to builder/single-disc-on-csr/
6. → **You test the rebuild**

## What You'll Do

**After agent commits the layer:**

1. Download from builder (or pull latest)
2. Test the rebuilt v0.1.2
3. Report movie flicker details

## Step 1: Wait for Agent to Build

Agent is building v0.1.2 layer automatically:
- Analyzed working v0.1.2 bin (done)
- Extracting DSKCG-stripped fields
- Writing build script with validation
- Generating layer
- Committing to builder/

**You'll be notified when ready to test.**

## Step 2: Pull Latest and Test

After agent commits v0.1.2 layer, download and test using the builder:

```bash
cd ~/Final-Fantasy-7-Modding
git pull --ff-only

# The builder will have the new v0.1.2 layer
# Test via https://individualcontributor.dev/builder/
# Or build locally:

python3 scripts/apply_layer.py \
  workspace/pristine/FINALFANTASY7_D1.bin \
  builder/single-disc-on-csr/layers/disc1.layer.json \
  -o workspace/test-v012.bin

# Apply movies + endings (agent will provide exact commands)
```

**Test checklist:**
- [ ] Game boots
- [ ] Disc 1 content plays (up to LOST2)
- [ ] Disc 1→2 transition works (no "Insert Disc 2" prompt)
- [ ] Break scene plays at COS_BTM2
- [ ] Music on LOST2 field
- [ ] Ending plays (note if audio flickers)
- [ ] LOSLAKE1 movie (field 637) - note if audio flickers

## Step 3: Report Results

Paste evidence:
```
✅ or ❌ for each test checklist item
Movie flicker details (which movies, when)
Any other issues
```

Then commit evidence:
```bash
git add docs/INSTRUCTIONS.md
git commit -m "ops: Tested v0.1.2 rebuild - [PASS/FAIL]"
git push
```

Agent will investigate movie flicker root cause and build v0.1.41 with the fix.

## Why This Approach

- **Agent builds automatically** (no manual exports, no manual scripts)
- **Validation built-in** (record count, size, decompression)
- **v0.1.2 was tested and works** (except movie flickers)
- **Rollback to known-good** before fixing the remaining issue
