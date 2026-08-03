# Task: No-swap — combine Ask-fixed + SNOVA v3 on one work bin

## Done

- Makou Ask-for-disc removal: DuckStation PASS (console untested)
- Supernova on D1: DuckStation PASS with inject v3
  - SNOVA raw-copy + BATTLE.X hardcoded LBA remap (17 entries)
  - Finding: docs/findings/2026-08-03-noswap-snova-injector.md
  - PASS note: docs/findings/2026-08-03-noswap-supernova-ds-pass.md

## Goal this turn

One clean D1 work image with both:
1. Makou Ask removals (from current noswap_work)
2. SNOVA v3 inject (files + BATTLE.X LBA patch)

Then quick smoke: new game intro OK + one former disc-ask OK + Supernova still OK if save available.

## Build

    cd Final-Fantasy-7-Modding
    git pull --ff-only

    # start from Ask-fixed work (backup first)
    cp -f workspace/iso-extract/ff7_d1_noswap_work.bin \
          workspace/iso-extract/ff7_d1_noswap_work.pre_snova.bak

    python3 mods/no-swap/scripts/inject_snova_d3_to_d1.py \
      --d1 workspace/iso-extract/ff7_d1_noswap_work.bin \
      --d3 workspace/pristine/FINALFANTASY7_D3.bin \
      --in-place

Must print:
- raw-copy + BATTLE.X LBA patch v3
- verify: BATTLE.X 17 LBA entries remapped
- verify: all SNOVA files match D3

If work bin already has SNOVA from an older attempt: restore bak or rebuild Ask edits on pristine, then inject once.

## Playtest smoke

1. New game to intro + first field
2. One former disc-ask hub (no Ask UI, continues)
3. Supernova if late save handy (should still PASS)

## Evidence

    Combined bin: path
    Tool verify v3: yes/no
    New game: PASS/FAIL
    Disc-ask: PASS/FAIL
    Supernova (if tested): PASS/FAIL/not tested

Say check. No pack ship this turn unless you want it.

## Notes

- Do not commit .bin images
- Engine MOVIE/DSKCG stubs stay abandoned
- Next after combine: CSR manip movie path / pack wiring
