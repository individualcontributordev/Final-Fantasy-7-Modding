# Task: No-swap — retest Supernova (v3 BATTLE.X LBA remap)

## Why v1/v2 failed

Copying SNOVA/ onto D1 is not enough. BATTLE.X hardcodes absolute D3 sector
numbers for SNOVA0-15 and LASBOSS3. The effect still read the old D3 LBAs
(empty/wrong on D1) → SFX path could tick, battle graphics wait forever.

## Fix v3 (pushed)

mods/no-swap/scripts/inject_snova_d3_to_d1.py

1. Raw-copy D3 SNOVA block (+570 sectors, EDC kept)
2. Patch decompressed BATTLE.X LBA table (17 entries), recompress, replace

Offline verified: table LBAs == find_file LBAs for all 17 assets.

## Build (must rebuild)

    cd Final-Fantasy-7-Modding
    git pull --ff-only
    cp -f workspace/pristine/FINALFANTASY7_D1.bin workspace/iso-extract/ff7_d1_snova_test.bin
    python3 mods/no-swap/scripts/inject_snova_d3_to_d1.py \
      --d1 workspace/iso-extract/ff7_d1_snova_test.bin \
      --d3 workspace/pristine/FINALFANTASY7_D3.bin \
      --in-place

Must print:
- raw-copy + BATTLE.X LBA patch v3
- verify: BATTLE.X 17 LBA entries remapped
- verify: all SNOVA files match D3

Do not reuse v1/v2 images.

## Playtest

DuckStation final battle / force Supernova.

| PASS | FAIL |
|------|------|
| Effect finishes, battle resumes | Freeze after SFX again |

## Evidence

    Tool: v3 yes/no (paste verify lines)
    Supernova DS: PASS/FAIL
    Notes:

Say check.

## If still FAIL

Then try battle stub (force-complete safer effect) for console pack — file
inject path exhausted for SNOVA LBA table known sites.

Do not commit .bin images.
