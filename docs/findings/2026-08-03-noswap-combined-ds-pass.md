# Finding: No-swap combined Ask + SNOVA D1 DuckStation PASS

**Date:** 2026-08-03
**Status:** confirmed on DS

## Result

Single Disc 1 work image with:

1. Makou removal of Ask-for-disc (DSKCG) field script sites
2. inject_snova_d3_to_d1.py v3 (SNOVA files + BATTLE.X LBA remap)

**PASS** for disc-change hubs and Supernova (prior smoke); combined image
reported working by playtester.

Local paths (not in git):

- workspace/iso-extract/ff7_d1_noswap_work.bin
- workspace/iso-extract/ff7_d1_noswap_work.pre_snova.bak

## Recipe (rebuild)

1. Pristine D1 -> work bin
2. Makou: remove Ask-for-disc per inventory findings (keep post-Ask jumps/flags)
3. Once: python3 mods/no-swap/scripts/inject_snova_d3_to_d1.py --d1 WORK --d3 D3 --in-place
4. Expect: raw-copy + BATTLE.X LBA patch v3; 17 LBA entries remapped

## Next

Document recipe in mods/no-swap; CSR movie whitelist; later pack/console.
