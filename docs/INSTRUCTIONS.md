# Task: No-swap — console smoke + keep recipe/pack wiring

## Done this session

- Clean rebuild recipe: mods/no-swap/README.md
- FMV wait vs wrong stream: docs/findings/2026-08-03-noswap-fmv-wait-vs-stream.md
  (wrong FMV often ends early; List/manip wait may still match duration)
- Pack wiring scaffold: mods/no-swap/scripts/build_clean_d1_layer.py
  (ic-layer from work vs pristine; manifest entry enabled:false)
- DS: Ask PASS, Supernova v3 PASS, combined PASS

## Console smoke (you — item 3)

Combined image path on your machine (after recipe):
workspace/iso-extract/ff7_d1_noswap_work.bin

| Platform | Notes |
|----------|--------|
| MiSTer PSX | Prefer FILE load of grown image first |
| Optical / PS2 | Repair Mode2 EDC/ECC on new SNOVA sectors before burn (docs/07-hardware-burn.md). Zero EDC on new dir/path meta may need full-disc repair tool. |

Minimum console checks:

1. New game reaches first field
2. One former disc-ask continues without Ask UI
3. Supernova completes if you can reach final battle

## Pack wiring (item 4) — after your work bin is combined

    python3 mods/no-swap/scripts/build_clean_d1_layer.py \
      --work workspace/iso-extract/ff7_d1_noswap_work.bin \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin

Then (when ready to publish later):

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base clean \
      --addon no-swap-clean-v0.0.0-dev

Leave enabled:false until full-run + console confidence.

## Evidence

    Console platform: MiSTer / PS2 / other / skipped
    New game: PASS/FAIL/not tested
    Disc-ask: PASS/FAIL/not tested
    Supernova: PASS/FAIL/not tested
    Layer build: ran / skipped (size notes)
    Notes:

Say check.

## Out of scope this turn

- CSR movie whitelist inject (default: try without; FMV wait finding)
- enabled:true public ship
