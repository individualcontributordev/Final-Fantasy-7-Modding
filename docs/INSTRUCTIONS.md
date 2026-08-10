# Task: Confirm fanfare-skip v0.1.6 (shipped patch)

## Result already in (skip-setup smoke)

Operator on BATRES `j 801B03B0 @ 801B02E0` (+ s4=0 + nop 7254):

- **No** win animations  
- **No** fanfare music  
- Battle ends after final kill (rewards path continues)

That is the intended product behavior. Packaged as **fanfare-skip-v0.1.6**.

## What 0.1.6 changes

`BATTLE/BATRES.X` only (same bytes all discs):

| VA | Patch |
|----|-------|
| **801B02E0** | force `j 801B03B0` (skip ceremony setup) |
| 801B028C | nop `jal 800A7254` |
| 801B02F8 / 032C / 03A0 | `ori s4,0,0` |

Does **not** touch FAN2.SND or BATTLE.X `800A2974` stub from 0.1.5.

Packs: `builder/fanfare-skip-v0.1.6` (+ on-csr / on-highwind). Manifest: 0.1.5 off, 0.1.6 on.

## Build play image

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
python3 scripts/apply_layer.py \
  workspace/pristine/FINALFANTASY7_D1.bin \
  builder/fanfare-skip-v0.1.6/layers/disc1.layer.json \
  -o workspace/iso-extract/ff7_d1_fanfare_skip_v016.bin
```

## Play / confirm

1. DuckStation → `workspace/iso-extract/ff7_d1_fanfare_skip_v016.bin`
2. Win **two** normal random battles.
3. Optionally one boss if easy.

## Evidence

```
Image: ff7_d1_fanfare_skip_v016.bin  (layer fanfare-skip-v0.1.6)

Battle 1:
  fanfare: YES/NO
  win poses: YES/NO
  rewards/exp/items OK: YES/NO
  return to field OK: YES/NO
  freeze: YES/NO

Battle 2:
  same: OK / PROBLEM (notes)

notes:
ship ready?: YES/NO
```

## When done

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
git add docs/INSTRUCTIONS.md
git commit -m "ops: confirm fanfare-skip v0.1.6"
git push
```

Then say **check**.

Do **not** commit .bin images.
