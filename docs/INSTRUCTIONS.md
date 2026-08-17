# Task: Rebuild Single-Disc v0.1.2 (Rollback from v0.1.40)

## Context

You tested the manually-built bin at `/Users/david.morton/Downloads/ff7-d1-csr-sd-mov-end.bin` and confirmed it works (disc 1→2 transition, break scene, gameplay complete). The only issues are movie audio flickers (ending + loslake1). This bin matches the v0.1.2 build pattern.

Versions 0.1.3 through 0.1.40 introduced regressions. We're rolling back to v0.1.2, then fixing the movie flickers in v0.1.41.

## What You'll Do

1. Open the working v0.1.2 bin in Makou Reactor
2. Export 3 field files (BLACKBGB, BLACKBGE, BLACKBG3) that have DSKCG removed
3. Build a fresh v0.1.2 layer from those exports
4. Test the rebuilt v0.1.2
5. Report back for movie flicker investigation

## Step 1: Export DSKCG-Stripped Fields from Working Bin

**Open Makou Reactor:**
```bash
# Your working bin path:
/Users/david.morton/Downloads/ff7-d1-csr-sd-mov-end.bin
```

**Export these 3 fields** (File → Export → Field):
1. **BLACKBGB** (Field ID 103) → Save as `workspace/v012-exports/BLACKBGB.DAT`
2. **BLACKBGE** (Field ID 104) → Save as `workspace/v012-exports/BLACKBGE.DAT`
3. **BLACKBG3** (Field ID 105) → Save as `workspace/v012-exports/BLACKBG3.DAT`

**Why:** These 3 fields had all 19 DSKCG operations removed. We need the exact bytes from your working bin.

## Step 2: Create Workspace Directory

```bash
cd ~/Final-Fantasy-7-Modding
mkdir -p workspace/v012-exports
mkdir -p workspace/v012-build
```

## Step 3: Build v0.1.2 Layer

Once you've exported the 3 fields above, run this build script:

```bash
cd ~/Final-Fantasy-7-Modding

python3 << 'EOF'
import sys
sys.path.insert(0, 'scripts')
from pathlib import Path
from disc_sources import find_csr_layer
from apply_layer import load_layer, apply_layer_to_bin
from put_field_dat import inject_field
from bin_diff_to_layer import generate_layer_from_diff
from psx_mode2_iso import PSXMode2ISO

# Paths
pristine = Path("workspace/pristine/FINALFANTASY7_D1.bin")
csr_d1 = find_csr_layer(1)
csr_d2 = find_csr_layer(2)
work = Path("workspace/v012-build/work.bin")
final = Path("workspace/v012-build/single-disc-v0.1.2-test.bin")
layer_out = Path("builder/single-disc-on-csr/layers/disc1.layer.json")

# Step 1: Start with pristine D1
print("Step 1: Copy pristine D1...")
work.parent.mkdir(parents=True, exist_ok=True)
work.write_bytes(pristine.read_bytes())

# Step 2: Apply CSR D1 layer (174 field edits)
print("Step 2: Apply CSR D1 layer...")
csr_d1_data = load_layer(csr_d1)
apply_layer_to_bin(work, csr_d1_data)

# Step 3: Overlay CSR D2 fields (prefer D2 for these)
print("Step 3: Overlay CSR D2 fields (LOST2, CANON_2)...")
# Apply CSR D2 layer to a temp bin, then extract LOST2 and CANON_2
temp_d2 = Path("workspace/v012-build/temp_d2.bin")
temp_d2.write_bytes(pristine.read_bytes())
csr_d2_data = load_layer(csr_d2)
apply_layer_to_bin(temp_d2, csr_d2_data)

# Extract LOST2 and CANON_2 from temp D2 bin
iso_d2 = PSXMode2ISO(temp_d2)
lost2 = iso_d2.read_file_by_name("FIELD/LOST2.DAT")
canon2 = iso_d2.read_file_by_name("FIELD/CANON_2.DAT")

# Inject into work bin
iso_work = PSXMode2ISO(work)
inject_field(work, "LOST2", lost2)
inject_field(work, "CANON_2", canon2)

# Step 4: Inject DSKCG-stripped fields from your working bin exports
print("Step 4: Inject DSKCG-stripped fields...")
blackbgb = Path("workspace/v012-exports/BLACKBGB.DAT").read_bytes()
blackbge = Path("workspace/v012-exports/BLACKBGE.DAT").read_bytes()
blackbg3 = Path("workspace/v012-exports/BLACKBG3.DAT").read_bytes()

inject_field(work, "BLACKBGB", blackbgb)
inject_field(work, "BLACKBGE", blackbge)
inject_field(work, "BLACKBG3", blackbg3)

# Step 5: Generate layer from diff
print("Step 5: Generate layer...")
generate_layer_from_diff(
    pristine,
    work,
    layer_out,
    version="0.1.2",
    description="Single-disc v0.1.2 rollback: CSR D1 base + D2 LOST2/CANON_2 + DSKCG stripped"
)

print(f"\n✅ Layer created: {layer_out}")
print(f"   Records: Check the JSON for field count")

# Step 6: Create test bin
print("\nStep 6: Create test bin...")
final.write_bytes(pristine.read_bytes())
apply_layer_to_bin(final, load_layer(layer_out))

print(f"\n✅ Test bin: {final}")
print("\nNext: Apply manip-movies layer + endings layers, then test")

EOF
```

## Step 4: Apply Additional Layers

The v0.1.2 working bin also includes:
- **manip-movies** (moved Disc 2/3 movies to Disc 1)
- **endings** (ending credits layers)

```bash
cd ~/Final-Fantasy-7-Modding

# Check which movie + ending layers exist
ls -1 builder/single-disc-*/layers/disc1.layer.json | grep -E "(manip-movies|endings)"

# Report the list — Agent will provide next apply commands
```

## Step 5: Test the Rebuilt v0.1.2

Burn `workspace/v012-build/single-disc-v0.1.2-test.bin` (or test in DuckStation).

**Test checklist:**
- [ ] Game boots
- [ ] Disc 1 content plays (up to LOST2)
- [ ] Disc 1→2 transition works (no "Insert Disc 2" prompt)
- [ ] Break scene plays at COS_BTM2
- [ ] Music on LOST2 field
- [ ] Ending plays (note if audio flickers)
- [ ] LOSLAKE1 movie (field 637) - note if audio flickers

## Step 6: Report Results

Paste evidence:
```
✅ or ❌ for each test checklist item
Movie flicker details (which movies, when)
Any other issues
```

Then Agent will investigate the movie flicker root cause and build v0.1.41 with the fix.

## Why This Approach

- **v0.1.2 was tested and works** (except movie flickers)
- **v0.1.3-v0.1.40 broke disc transition** (regressions)
- **Rollback to known-good** before fixing the remaining issue
- **Movie flickers are separate** from disc transition (can fix after rollback)

## Files Modified

- `mods/single-disc/VERSION` → `0.1.2`
- `mods/single-disc/CHANGELOG.md` → Added rollback entry
- `builder/single-disc-on-csr/layers/disc1.layer.json` → Will be regenerated
