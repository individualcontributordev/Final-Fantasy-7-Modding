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

**Verification complete (full stack):**
- ✅ All FIELD files match working bin EXACTLY
- ✅ Complete bin size: 766,340,400 bytes (same as working bin)
- ✅ All critical fields verified byte-for-byte
- ✅ Movies and endings included (manip-movies + 7 ending parts)

**Layer stack:**
1. Field layer: 96,497 records (CSR D1 + D2 overlays + DSKCG stripped)
2. Manip-movies: 841,849 records (Disc 2/3 movies → Disc 1)
3. Endings (7 parts): 3,271,675 records total

**Total: 4,210,021 records applied**

## What You Do

### Step 1: Pull Latest

```bash
cd ~/Final-Fantasy-7-Modding
git pull --ff-only
```

### Step 2: Build Complete Test Disc

Apply all required layers (fields + movies + endings):

```bash
cd ~/Final-Fantasy-7-Modding

# This script applies all layers in the correct order
python3 << 'EOF'
import sys
sys.path.insert(0, 'scripts')
from pathlib import Path
from apply_layer import apply_layer
import json

pristine = Path("workspace/pristine/FINALFANTASY7_D1.bin")
output = Path("workspace/test-v012-complete.bin")

print("Building complete v0.1.2 with movies and endings...")
img = bytearray(pristine.read_bytes())

# Layer 1: Field changes
print("\n1. Applying field layer...")
layer = json.loads(Path("builder/single-disc-on-csr/layers/disc1.layer.json").read_text())
apply_layer(img, layer)
print(f"   Applied {len(layer['records']):,} records")

# Layer 2: Manip-movies (Disc 2/3 movies moved to Disc 1)
print("\n2. Applying manip-movies layer...")
layer = json.loads(Path("builder/single-disc-csr-manip-movies-v0.1.4/layers/disc1.layer.json").read_text())
apply_layer(img, layer)
print(f"   Applied {len(layer['records']):,} records")

# Layer 3: Ending movies (parts 1-7)
print("\n3. Applying ending layers...")
for part in range(1, 8):
    layer = json.loads(Path(f"builder/single-disc-endings-v0.1.0-part{part}/layers/disc1.layer.json").read_text())
    apply_layer(img, layer)
    print(f"   Part {part}: {len(layer['records']):,} records")

output.write_bytes(img)
print(f"\n✅ Complete v0.1.2 bin: {output}")
print(f"   Size: {len(img):,} bytes ({len(img) // 2352:,} sectors)")
EOF
```

### Step 3: Test in DuckStation

Load `workspace/test-v012-complete.bin` in DuckStation.

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
