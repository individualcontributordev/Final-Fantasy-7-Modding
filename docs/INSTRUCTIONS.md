# Task: No-disc-swap — apply ioslake3 movie trim (optional polish)

## Root cause (checked)

ioslake3 S0 Main at GameMoment 1398:

- Set next movie No57 D1 = ONTRAIN.MOV (D2 wants loslake1)
- Set next movie No58 D1 = OPENING.BIN (D2 wants lslmv)
- Real files D2-only: LOSLAKE1.MOV, LSLMV.STR

Missing FMV + Bugenhagen idle is expected on D1-only without trim/copy.
Not a freeze; Jump to loslake1 should still be reachable after waits if MOVIE returns.

Finding: docs/findings/2026-08-03-noswap-ioslake3-missing-fmv.md
Recipe: mods/no-disc-swap/patches/field-movie-trims.md

## Your Makou edit (recommended polish)

Work bin with Ask+SNOVA (or rebuild per mods/no-disc-swap/README.md).

Map ioslake3, script S0 Main, block GameMoment == 1398:

1. Delete both Set next movie lines
2. Delete both Play movie lines
3. Keep all Execute script, Wait, and Jump to loslake1

Smoke on DuckStation: scene progresses to loslake1 without long blank stare.

## Then republish pack

    python3 mods/no-disc-swap/scripts/build_clean_d1_layer.py \
      --work workspace/iso-extract/ff7_d1_noswap_work.bin \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin

Ensure manifest enabled true for no-disc-swap-clean-v0.0.0-dev, then:

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base clean \
      --addon no-disc-swap-clean-v0.0.0-dev

Commit builder layer + push, then new builder zip / burn if needed.

## Evidence

    Makou trim applied: yes/no
    DS advance to loslake1: PASS/FAIL
    Layer rebuilt + pushed: yes/no
    Notes:

Say check.

## If you prefer leave vanilla

No edit required for full-run if Jump already fires; missing FMV only.
