# Task: No-swap — retest Supernova (SNOVA raw-copy v2)

## Result so far

- Ask-for-disc Makou: DS PASS
- SNOVA inject v1 (user-data rewrite, zero EDC): FAIL
  - Heard Supernova SFX, then battle frozen; music kept playing after SFX ended
- SNOVA inject v2 raw-copy: preserves D3 EDC/ECC on file sectors; fixes MSF only
  - Offline: SNOVA0 sector sub+payload+edc match D3: True

## Goal

Rebuild with v2 and confirm Supernova finishes (battle unfreezes).

## Build (must rebuild — do not reuse v1 image)

    cd Final-Fantasy-7-Modding
    git pull --ff-only

    # A: pristine + SNOVA (Supernova smoke)
    cp -f workspace/pristine/FINALFANTASY7_D1.bin workspace/iso-extract/ff7_d1_snova_test.bin
    python3 mods/no-swap/scripts/inject_snova_d3_to_d1.py \
      --d1 workspace/iso-extract/ff7_d1_snova_test.bin \
      --d3 workspace/pristine/FINALFANTASY7_D3.bin \
      --in-place

Must print:
- wrote ... (raw-copy v2)
- SNOVA0 sector sub+payload+edc match D3: True
- verify: all SNOVA files match D3

If injecting on Ask-fixed work, restore bak first (no double inject):

    cp -f workspace/iso-extract/ff7_d1_noswap_work.pre_snova.bak \
          workspace/iso-extract/ff7_d1_noswap_work.bin
    python3 mods/no-swap/scripts/inject_snova_d3_to_d1.py \
      --d1 workspace/iso-extract/ff7_d1_noswap_work.bin \
      --d3 workspace/pristine/FINALFANTASY7_D3.bin \
      --in-place

## Playtest

DuckStation on the NEW image, final battle / force Supernova.

| PASS | FAIL |
|------|------|
| Effect plays and battle resumes | SFX + freeze again, or worse |

## Evidence

    Tool: raw-copy v2 yes/no (paste last 3 lines)
    Image: snova_test / noswap_work
    Supernova DS: PASS/FAIL
    Notes:

Say check.

## Notes

- v1 zeroed EDC/ECC — likely why graphics stalled after audio
- D3 SNOVA is one contiguous 570-sector block; v2 memcpy that block
- Do not commit .bin images
