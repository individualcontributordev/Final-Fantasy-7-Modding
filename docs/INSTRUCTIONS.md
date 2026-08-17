# TASK: Restore full single-disc layer (CSR D1+D2+D3 merge + DSKCG + LOST2 + SNOVA)

**Status:** NEEDS REWRITE - Architecture was misunderstood
**Agent session:** 2026-08-17
**Target:** v0.1.40 single-disc layer with smart CSR D1/D2/D3 merge + DSKCG + LOST2 + SNOVA

## Problem

v0.1.39 layer contains **only** the LOST2 IFUW music patch (16,726 records). It's **missing**:
- CSR D1 field changes (174 files)
- CSR D2/D3 field changes merged onto D1 (77 files, with conflict resolution)
- All 19 DSKCG (Ask for disc) removals
- SNOVA inject from D3

Regression introduced in commit 7fd1dc2 (Aug 16) when versioned directories were deleted.

## Architecture (CORRECTED)

**Critical insight: The same field may be edited on D1 AND D2 for different game moments.**

Example: `BLACKBGB` (field 103):
- CSR D1 version: Used when player visits during Disc 1 gameplay
- CSR D2 version: Used when player visits during Disc 2 gameplay
- **These are DIFFERENT edits** - cannot just overwrite D1 with D2!

### CSR Multi-Disc Field Edits

From `docs/findings/2026-08-06-csr-multi-disc-field-edits.md`:
- 174 fields edited on CSR D1
- 71 fields edited on CSR D2
- 4 fields edited on CSR D3
- **10 fields edited on BOTH D1 and D2** with different content

### Field Merge Policy

From `mods/single-disc/patches/csr-field-disc-prefer.txt`:
- **prefer-D1**: Keep CSR D1 version (e.g., `BLACKBGB`, `DEL1`, `LOSIN2`)
- **prefer-D2**: Use CSR D2 version (e.g., `LOST2`, `CANON_2`)
- **review**: 7 fields need manual Makou comparison before merging

The single-disc D1 image must have:
1. CSR D1 field edits (174 files)
2. CSR D2/D3 field edits (77 files from `csr-d2d3-field-merge-on-d1.md`)
3. Conflict resolution: Follow `csr-field-disc-prefer.txt` for the 10 collisions
4. DSKCG removals (19 operations)
5. LOST2 IFUW patch
6. SNOVA inject

## Solution Approach

### Option A: Script-Based Merge (RECOMMENDED if script exists)

```bash
cd ~/Final-Fantasy-7-Modding
git pull --ff-only

# Start with pristine D1
cp -f workspace/pristine/FINALFANTASY7_D1.bin workspace/iso-extract/ff7_d1_single_disc_work.bin

# Apply CSR D1 layer (all CSR story fixes)
python3 scripts/apply_layer.py \
  --bin workspace/iso-extract/ff7_d1_single_disc_work.bin \
  --layer ../Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json \
  --in-place
```

### 2. Makou — remove every Ask for disc

**Open work image** (not pristine) in Makou Reactor.

For each field, delete the "Ask for disc" (DSKCG) operations **only**. Keep Bit clears, conditions, and map jumps after each ask.

**Maps to edit:**

| Map | Field # | Script | Lines | Asks |
|-----|---------|--------|-------|------|
| BLACKBGB | 103 | init / S0 - Main | 43, 64, 73, 95 | 4 |
| BLACKBGE | 106 | AD / Script 4 | 2 | 1 |
| BLACKBG3 | 95 | p8 / S1 - Talk | 27, 33, 42, 52, 58, 87, 100, 113, 132, 166, 178, 185, 207 | 13 |
| BLACKBG3 | 95 | p7 / S1 - Talk | 25 | 1 |

**Total DSKCG operations to remove: 19**

**After each field edit:** Save FIELD back into the work bin so the ISO is updated.

**Verification:** Run Find All on "Ask for disc" in the work image. Should return 0 results.

### 3. SNOVA + BATTLE.X inject

```bash
cd ~/Final-Fantasy-7-Modding

cp -f workspace/iso-extract/ff7_d1_single_disc_work.bin \
      workspace/iso-extract/ff7_d1_single_disc_work.pre_snova.bak

python3 mods/single-disc/scripts/inject_snova_d3_to_d1.py \
  --d1 workspace/iso-extract/ff7_d1_single_disc_work.bin \
  --d3 workspace/pristine/FINALFANTASY7_D3.bin \
  --in-place
```

**Must print:**
- raw-copy + BATTLE.X LBA patch v3
- verify: BATTLE.X 17 LBA entries remapped
- verify: all SNOVA files match D3

### 4. Build v0.1.40 base layer against pristine

This generates offset/hex records for all changes (CSR fields + DSKCG removals + SNOVA):

```bash
cd ~/Final-Fantasy-7-Modding

# Backup v0.1.39 for reference
cp builder/single-disc-on-csr/layers/disc1.layer.json \
   builder/single-disc-on-csr/layers/disc1.layer.json.v0.1.39.bak

# Build new layer
python3 scripts/bin_diff_to_layer.py \
  --base workspace/pristine/FINALFANTASY7_D1.bin \
  --work workspace/iso-extract/ff7_d1_single_disc_work.bin \
  --out builder/single-disc-on-csr/layers/disc1.layer.json \
  --id single-disc-on-csr-v0.1.40-disc1 \
  --description "Single-disc v0.1.40: CSR fields + DSKCG removals + SNOVA (no LOST2 yet)"
```

**Expected output:**
- Record count should be large (~850k+ records: CSR field changes + DSKCG + SNOVA)

### 5. Merge LOST2 patch into layer

The v0.1.39 layer has the LOST2 IFUW patch (16,726 records). Merge those into the v0.1.40 layer:

```bash
cd ~/Final-Fantasy-7-Modding

python3 << 'EOF'
import json
from pathlib import Path

# Load v0.1.39 LOST2-only layer (from backup)
v39_layer = json.loads(Path("builder/single-disc-on-csr/layers/disc1.layer.json.v0.1.39.bak").read_text())
lost2_records = v39_layer["records"]
print(f"v0.1.39 LOST2 records: {len(lost2_records)}")

# Load v0.1.40 base layer (DSKCG + SNOVA but no LOST2)
v40_path = Path("builder/single-disc-on-csr/layers/disc1.layer.json")
v40_layer = json.loads(v40_path.read_text())
print(f"v0.1.40 base records: {len(v40_layer['records'])}")

# Merge: v40 base + v39 LOST2
all_records = v40_layer["records"] + lost2_records
print(f"Merged records: {len(all_records)}")

# Update layer
v40_layer["id"] = "single-disc-on-csr-v0.1.40-disc1"
v40_layer["description"] = "Single-disc v0.1.40: Complete DSKCG removals + LOST2 music patch + SNOVA"
v40_layer["records"] = all_records
v40_layer["stats"]["records"] = len(all_records)
v40_layer["stats"]["changedBytes"] = len(all_records)

# Write merged layer
v40_path.write_text(json.dumps(v40_layer, indent=2))
print(f"\n✅ Merged layer saved: {v40_path}")
print(f"Total records: {len(all_records)}")
EOF
```

### 6. Update pack version and manifest

```bash
cd ~/Final-Fantasy-7-Modding

# Update VERSION file
echo "0.1.40" > mods/single-disc/VERSION

# Update pack.json
python3 << 'EOF'
import json
from pathlib import Path

pack_path = Path("builder/single-disc-on-csr/pack.json")
pack = json.loads(pack_path.read_text())
pack["version"] = "0.1.40"
pack["blurb"] = "Play the whole game from one Disc 1 image on CSR. v0.1.40: Complete DSKCG removals + LOST2 music patch."
pack_path.write_text(json.dumps(pack, indent=2))
print("✅ Updated pack.json")
EOF

# Update manifest.json
python3 << 'EOF'
import json
from pathlib import Path

manifest_path = Path("builder/manifest.json")
manifest = json.loads(manifest_path.read_text())

for addon in manifest["addons"]:
    if addon["id"] == "single-disc-on-csr":
        addon["version"] = "0.1.40"
        addon["blurb"] = "Play the whole game from one Disc 1 image on CSR. v0.1.40: Complete DSKCG removals + LOST2 music patch."
        break

manifest_path.write_text(json.dumps(manifest, indent=2))
print("✅ Updated manifest.json")
EOF
```

### 7. Commit and push

```bash
cd ~/Final-Fantasy-7-Modding

git add -A
git commit --author="individualcontributordev <contributorindividual@gmail.com>" -m "single-disc v0.1.40: Restore full DSKCG removals + LOST2 patch

Regression fix from v0.1.39 (LOST2-only) and v0.1.38 refactor.

Combined changes:
- All 19 Ask-for-disc (DSKCG) removals from fields 103, 106, 95
- LOST2 IFUW music patch (16,726 records) for D1→D2 break scene
- SNOVA + BATTLE.X inject for final battle

This is the first complete single-disc layer since the Aug 16 refactor.

Verified in Makou: Field 103 has no DSKCG operations."

git push origin main
```

### 8. Test

Wait ~5 min for CDN propagation, then test at https://individualcontributor.dev/builder/

1. Clear pack cache (DevTools Console: `localStorage.clear(); location.reload()`)
2. Build CSR + Single-disc
3. Open in Makou Reactor: verify Field 103 has no "Ask for disc" ops
4. Test in DuckStation: play to Kalm flashback end, should continue without disc swap prompt

## Paste Evidence Here
