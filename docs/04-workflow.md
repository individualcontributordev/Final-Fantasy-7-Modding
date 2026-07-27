# Edit → Rebuild → Test Workflow

General loop for **PSX disc patches** (engine binaries, reinserted files, full ISO saves).

Use this for every hardware-impacting change.

## Overview

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────┐
│ FIELD.BIN   │───▶│ Ghidra patch │───▶│ Recompress  │───▶│ Import   │
│ .dec        │    │ (code cave)  │    │ GZIPPS      │    │ to ISO   │
└─────────────┘    └──────────────┘    └─────────────┘    └────┬─────┘
                                                                 │
                    ┌──────────────┐    ┌─────────────┐         │
                    │ Document in  │◀───│ Emulator    │◀────────┘
                    │ patches/     │    │ test        │
                    └──────────────┘    └─────────────┘
```

## Step-by-step

### 1. Backup

```bash
cp workspace/iso-extract/ff7_disc1.bin workspace/iso-extract/ff7_disc1_pristine.bin
cp workspace/iso-extract/FIELD.BIN workspace/iso-extract/FIELD.BIN.pristine
```

### 2. Decompress (if starting fresh)

```bash
python3 scripts/decompress_field_bin.py workspace/iso-extract/FIELD.BIN
```

### 3. Patch

- Ghidra: edit `FIELD.BIN.dec` in place, or export patched binary
- Save as `FIELD.BIN.dec.patched`
- Record offset, old bytes, new bytes in `docs/findings/YYYY-MM-DD-description.md` (and stub bytes under `mods/<mod>/patches/` when shipping)

### 4. Recompress

```bash
python3 scripts/compress_field_bin.py \
  workspace/iso-extract/FIELD.BIN.dec.patched \
  workspace/iso-extract/FIELD.BIN \
  workspace/iso-extract/FIELD.BIN.new
```

Preserves original 8-byte GZIPPS header from source `FIELD.BIN`.

### 5. Reinsert into ISO

**Makou:** Open ISO → (replace FIELD.BIN via tool) → Save ISO

**Manual:** CDmage import `FIELD.BIN.new` over existing at same LBA

**Important:** If compressed size grows beyond original sector allocation, ff7tk/Makou
relocates the file and updates the index. Small patches usually fit in place.

### 6. Test in emulator → FPGA → (optional) burn

1. **DuckStation Safe Mode** — fast iterate; RAM watches  
2. **MiSTer PSX** — high confidence Ghidra/Makou logic will work on PS1 hardware  
3. **Burn + PS2 MechaPwn** — when shipping or after disc-format/EDC changes ([07-hardware-burn.md](07-hardware-burn.md))

Use `ff7_disc1_test.bin` (copy of modified ISO) for (1)/(2).

| Test | Pass criteria |
|------|---------------|
| Boot | Game reaches title / new game |
| Field load | Can enter Sector 1 train station |
| Movement | No immediate crash walking |
| Encounters | Battles still trigger (eventually) |
| Regression | Scripts/dialogue still work on test map |

### 7. RAM verification (when patch is live)

In emulator memory viewer while walking on a hostile field:

- `0x8007173C` (Danger) increases
- `0x8009C540` (StepID) changes on encounter checks
- After field transition (post-patch): values should differ from unpatched run

## Test maps (disc 1)

| Map | Why |
|-----|-----|
| Opening train / Sector 1 | First hostile fields, fast to reach |
| Grass outside Midgar | Simple layout, encounters enabled |
| Safe room (inn, save point) | No encounters — crash = patch too aggressive |

## When something breaks

1. Revert to `FIELD.BIN.pristine` and recompress — does game work?
2. If yes: patch is the problem; bisect in Ghidra
3. If no: ISO import corrupted; re-copy pristine disc image

## Shipping to the disc builder

Diff the final image against the stack base (retail or CSR) into `ic-layer-v1` JSON.
Encounter packs: root [README.md](../README.md).
Stub bytes: `mods/field-random-encounters/patches/`.

## Patch log template

Create `docs/findings/YYYY-MM-DD-short-name.md`:

```markdown
# Patch: [name]

## Goal


## File
FIELD.BIN.dec @ offset 0x.........

## Changes
| Offset | Was | Now | Reason |
|--------|-----|-----|--------|

## Test result
- [ ] Boots
- [ ] Field load
- [ ] Encounters
- [ ] Notes
```
