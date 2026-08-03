# Finding: D3 SNOVA inject onto D1 (Mode2 grow)

**Date:** 2026-08-03
**Status:** tool verified offline; in-game Supernova playtest pending

## Summary

Supernova assets live only on retail D3 under SNOVA/ (17 files, ~1.15 MB).
D1 root had ~830 bytes padding — enough for one extra directory record.
Image grows by 570 sectors (~1.34 MB raw Mode2).

## Tool

mods/no-swap/scripts/inject_snova_d3_to_d1.py

- Appends SNOVA/ dir + files at end of volume
- Patches root dir, type-L/M path tables, PVD volume size + path table size
- Verifies via extract_file byte-match vs D3

## Offline result

SNOVA files=17 bytes=1149307
grow sectors 317787 -> 318357 (+570)
verify: all SNOVA files match D3

Test image (local only): workspace/iso-extract/ff7_d1_snova_test.bin

## Caveats

- EDC/ECC zero on new sectors — DuckStation OK; burn needs repair
- Path table insert is name-sorted under parent 1
- Do not double-inject (script aborts if SNOVA/SNOVA0.LZS exists)

## Next

Playtest Supernova on DuckStation; then inject onto Ask-fixed work bin.
