# Build and Verify Single-Disc v0.1.2

## Goal
Build a CSR + Single-disc v0.1.2 bin locally using the published layers and verify it matches the working reference bin byte-for-byte.

## Prerequisites
- Working reference bin: `~/Downloads/ff7-d1-csr-sd-mov-end.bin` (766,340,400 bytes)
- Pristine disc: `workspace/pristine/FINALFANTASY7_D1.bin` (or `Final Fantasy VII (Disc 1).bin`)
- Both repos cloned as siblings:
  - `~/Final-Fantasy-7-CSR`
  - `~/Final-Fantasy-7-Modding`

## Steps

### 1. Build the bin using published layers

```bash
cd ~/Final-Fantasy-7-Modding

python3 scripts/verify_builder_config.py \
  --pristine workspace/pristine/FINALFANTASY7_D1.bin \
  --disc 1 \
  --base csr-v0.14.1 \
  --addon single-disc-on-csr \
  --addon single-disc-v0.1.2-part2 \
  --addon single-disc-v0.1.2-part3 \
  --addon single-disc-v0.1.2-part4 \
  --addon single-disc-v0.1.2-part5 \
  --addon single-disc-v0.1.2-part6 \
  --addon single-disc-v0.1.2-part7 \
  --addon single-disc-v0.1.2-part8 \
  --addon single-disc-v0.1.2-part9 \
  --addon single-disc-v0.1.2-part10 \
  --output workspace/local-build-v012.bin
```

Expected output:
```
Config: base=csr-v0.14.1 addons=['single-disc-on-csr', 'single-disc-v0.1.2-part2', ...] disc=1
Pristine: .../FINALFANTASY7_D1.bin
  OK base csr-v0.14.1 ← csr-v0.14.1/layers/disc1.layer.json (94148 records, ...)
  OK addon single-disc-on-csr ← single-disc-on-csr/layers/disc1.layer.json (414665 records)
  OK addon single-disc-v0.1.2-part2 ← ... (414665 records)
  ... parts 3-10 ...
Wrote workspace/local-build-v012.bin (766340400 bytes)
Stack:
  - base:csr-v0.14.1 (94148 records via cache/layer)
  - addon:single-disc-on-csr (disc1.layer.json, 414665 records)
  - addon:single-disc-v0.1.2-part2 (disc1.layer.json, 414665 records)
  ... parts 3-10 ...
PASS — builder config applies cleanly (4240789 total records)
```

### 2. Verify file size

```bash
ls -lh workspace/local-build-v012.bin
```

Expected: **766,340,400 bytes** (731 MB)

### 3. Compare to working reference bin

```bash
python3 scripts/compare_builder_download.py \
  workspace/local-build-v012.bin \
  ~/Downloads/ff7-d1-csr-sd-mov-end.bin
```

Expected output:
```
=== Builder Download vs Working Bin Analysis ===

Builder bin: workspace/local-build-v012.bin
  Size: 766,340,400 bytes (325,825 sectors)

Working bin: ~/Downloads/ff7-d1-csr-sd-mov-end.bin
  Size: 766,340,400 bytes (325,825 sectors)

✅ Sizes match

Comparing byte-by-byte...
✅ PERFECT MATCH - Files are identical!
```

### 4. Test in DuckStation

Transfer `workspace/local-build-v012.bin` to your Windows machine and test:
1. Load in DuckStation
2. Play to disc 1→2 transition
3. **Check:** Does "Save game?" screen appear?
4. **Check:** Does break scene at COS_BTM2 play correctly?

## Report Results

Post in chat:
1. File size of `workspace/local-build-v012.bin`: `_______ bytes`
2. Comparison result: `PERFECT MATCH` or `DIFFERENT`
3. DuckStation test result:
   - Save screen appears: YES / NO
   - Break scene plays: YES / NO
4. If different or broken, include the full output from step 3

## What This Tests

- **If PERFECT MATCH + works in DuckStation:** The layers are correct, builder website has an issue
- **If PERFECT MATCH + broken in DuckStation:** The working reference bin was never actually working
- **If DIFFERENT:** Agent's layer extraction or build process is broken
