# INSTRUCTIONS — Export LOST2 Ghidra data + prepare v0.1.36 playtest

## What happened

v0.1.35 fixed the LOST2 crash but music stayed silent. Root cause: script hit `RET` immediately after `MUSIC` opcode, preventing ambient `AKAO` opcodes from executing.

v0.1.36 patch created: replaces `RET` at offset `0x470` with `JMPF +0x24` to jump to ambient AKAO block at `0x497`.

## Your tasks

### Task 1: Export Ghidra data for LOST2 (one-time setup)

This creates a reference export for Agent to verify the patch and for future field script work.

**Prerequisites:**
- Ghidra installed with PSX plugin
- LOST2.DAT decompressed in `workspace/tmp/`

**Steps:**

1. **Extract LOST2.DAT from pristine D2:**

```bash
cd ~/Final-Fantasy-7-Modding
python scripts/extract_field_dat.py \
  --from pristine:2 \
  --field LOST2 \
  -o workspace/tmp/LOST2-d2-pristine.DAT
```

2. **Decompress it (field maps use LZS compression, not GZIP):**

```bash
cd ~/Final-Fantasy-7-Modding
python3 -c "
import sys
sys.path.insert(0, 'scripts')
from lzs import decompress_all_with_header
from pathlib import Path

dat = Path('workspace/tmp/LOST2-d2-pristine.DAT').read_bytes()
dec = decompress_all_with_header(dat)
Path('workspace/tmp/LOST2-d2-pristine.dec').write_bytes(dec)
print(f'Decompressed {len(dat)} -> {len(dec)} bytes')
print('Wrote workspace/tmp/LOST2-d2-pristine.dec')
"
```

3. **Import into Ghidra:**
   - Open Ghidra
   - File → Import File → Browse to `workspace/tmp/LOST2-d2-pristine.dec`
   - Format: **Raw Binary**
   - Language: **MIPS:LE:32:default**
   - Base address: **`0x00000000`** (file offsets match addresses directly)
   - Click OK → Skip analysis (field scripts are bytecode, not MIPS - decompiler won't work)
   - **Note:** The decompiler won't show code because these are script data bytes, not MIPS instructions

4. **Navigate to init/0 script:**
   - Navigation → Go To → `0x434` (this is the file offset where init/0 starts)
   - You should see bytes: `43 00 14 30 84 04 09 05 f0 00 ...`

5. **Select script region for export:**
   - Click at address `0x434`
   - Shift+Click at address `0x4F0` (selects ~188 bytes covering the full init/0 script)

6. **Export the selection:**
   - File → Export Program
   - Format: **ASCII**
   - Output file: `workspace/ghidra/LOST2-init-script-pristine-d2.txt`
   - Options: Check "Selection Only"
   - Include: Addresses and Bytes
   - Click OK

7. **Also export raw hex for verification:**
   - With the same range still selected (`0x434` to `0x4F0`)
   - Right-click → Copy Special → **Byte String**
   - Paste into: `workspace/ghidra/LOST2-init-script-pristine-d2.hex`
   - Save the file

8. **Commit the exports:**

```bash
cd ~/Final-Fantasy-7-Modding
git pull --ff-only
mkdir -p workspace/ghidra
git add workspace/ghidra/LOST2-init-script-*.txt
git add workspace/ghidra/LOST2-init-script-*.hex
git commit -m "Add Ghidra exports for LOST2 init/0 script (D2 pristine)

Exports cover offsets 0x434-0x4F0 (init/0 script section).

Reference for v0.1.36 JMPF patch verification and future field
script debugging. Includes ASCII listing with addresses and raw
hex byte string.

Exported from: workspace/pristine/FINALFANTASY7_D2.bin:FIELD/LOST2.DAT
Base: 0x00000000, Format: Data:LE:8" --author="individualcontributordev <contributorindividual@gmail.com>"
git push
```

**Paste the exports here** (first 20 lines of `.txt` and first 100 chars of `.hex`) so Agent can verify.

### Task 2: Build and playtest v0.1.36

1. **Build the disc:**

```bash
cd ~/Final-Fantasy-7-Modding

# Use builder site or manual layer application
# Stack: CSR v0.14.1 + single-disc-on-csr-v0.1.36 (the new layer)

# Manual build example:
python scripts/verify_builder_config.py \
  --pristine workspace/pristine/FINALFANTASY7_D1.bin \
  --disc 1 \
  --base csr-v0.14.1 \
  --addon single-disc-on-csr-v0.1.36 \
  --output workspace/tmp/sd-v036-test.bin
```

Or use https://individualcontributor.dev/builder/ with:
- Base: CSR v0.14.1
- Add-ons: Single-Disc v0.1.36 (should auto-select when v0.1.33 is on)

2. **Burn to disc or load in DuckStation**

3. **Playtest checklist:**

| Check | Location | Expected Result |
|-------|----------|-----------------|
| Reach LOST2 | Field #634 (Lost Forest disc transition area) | No crash (same as v0.1.35) |
| Forest music | LOST2 after entering | **Music plays** (not silent) |
| Ambient sounds | LOST2 background | Wind/forest ambient audio present |
| Save page | BLACKBGB (before/after LOST2) | Save page appears normally |

4. **Report results:**

```bash
cd ~/Final-Fantasy-7-Modding
git pull --ff-only

# If PASS (music plays):
echo "v0.1.36 PASS - LOST2 music + ambient working" >> docs/INSTRUCTIONS.md

# If FAIL (still silent):
echo "v0.1.36 FAIL - music still silent, details: <paste what you saw>" >> docs/INSTRUCTIONS.md

git add docs/INSTRUCTIONS.md
git commit -m "Playtest result: v0.1.36 LOST2 music" --author="individualcontributordev <contributorindividual@gmail.com>"
git push
```

**Paste evidence here:** Screenshot or text description of what happened in LOST2.

## Why this matters

The Ghidra exports let Agent see exact opcode sequences and offsets before writing patches, avoiding blind pattern-matching. Future field script patches will be faster and more accurate.

## Previous context

- v0.1.35 result: docs/findings/2026-08-13-v035-music-fail-save-ok.md
- v0.1.36 patch script: mods/single-disc/scripts/ship_v036.py
- Layer file: builder/single-disc-on-csr-v0.1.36-disc1.layer.json
