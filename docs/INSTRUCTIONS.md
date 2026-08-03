# Task: No-swap — playtest Supernova after SNOVA inject

## Done

- Makou: all Ask-for-disc removed on D1 work bin
- DuckStation disc-ask: PASS (console not tested)
- Finding: docs/findings/2026-08-03-noswap-makou-ask-ds-pass.md
- Engine FIELD MOVIE/DSKCG stubs: abandoned for playable bins
- SNOVA injector offline-verified: mods/no-swap/scripts/inject_snova_d3_to_d1.py
  - 17 files from D3, ~1.15 MB, grows image +570 sectors
  - extract_file round-trip OK on workspace/iso-extract/ff7_d1_snova_test.bin

## Goal this turn

Confirm Supernova does not freeze on D1-only in DuckStation.

### Build options

A — Supernova-only smoke (pristine + SNOVA), already local if kept:

    cp -f workspace/pristine/FINALFANTASY7_D1.bin workspace/iso-extract/ff7_d1_snova_test.bin
    python3 mods/no-swap/scripts/inject_snova_d3_to_d1.py       --d1 workspace/iso-extract/ff7_d1_snova_test.bin       --d3 workspace/pristine/FINALFANTASY7_D3.bin       --in-place

Load a late-game / final-battle save in DuckStation on that image.

B — Combined (Ask-fixed work + SNOVA), preferred once A works:

    cp -f workspace/iso-extract/ff7_d1_noswap_work.bin           workspace/iso-extract/ff7_d1_noswap_work.pre_snova.bak
    python3 mods/no-swap/scripts/inject_snova_d3_to_d1.py       --d1 workspace/iso-extract/ff7_d1_noswap_work.bin       --d3 workspace/pristine/FINALFANTASY7_D3.bin       --in-place

Must print: verify: all SNOVA files match D3
Refuse if SNOVA already present (use bak or rebuild).

### Playtest

1. DuckStation to final battle / force Supernova (save or cheat)
2. Attack must run without permanent freeze
3. If B: quick smoke new game + one former disc-ask map still OK

## Evidence

    Image used: snova_test / noswap_work+SNOVA / other:
    Tool verify line seen: yes/no
    Supernova DS: PASS/FAIL/not tested
    Notes (freeze point / black / crash):
    New game + disc-change (if B): PASS/FAIL/not tested

Say check. No pack ship this turn.

## Notes

- Makou cannot add ISO dirs. Injector (or CDmage) does SNOVA.
- New sectors have zero EDC/ECC — OK for DuckStation; repair before real burn.
- Do not commit .bin images.

## Out of scope

- FIELD MOVIE engine stubs
- CSR manip movie whitelist
- Publishing builder pack
