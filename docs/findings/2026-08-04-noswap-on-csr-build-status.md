# Finding: no-disc-swap-on-csr v0.1.1 build status

**Date:** 2026-08-04
**Status:** partial pack published for CSR+ path

## What was automated

Against **csr-v0.14.1** D1 baseline:

1. Applied Clean no-disc-swap FIELD trims for every noswap map **except BLACKBGB**
   (CSR does not touch those maps — bytes match pristine, safe overwrite).
2. Grew ISO size in-place for **LAS4_0.DAT** (+5) and **MD8_52.DAT** (+2)
   within existing sector allocation.
3. Left **FIELD.BIN** as CSR (no Clean 18-byte engine delta).
4. Ran **SNOVA + BATTLE.X LBA remap v3** (same as Clean pack).

Pack: builder/no-disc-swap-on-csr-v0.1.1/
Work: workspace/iso-extract/ff7_d1_csr_noswap_work.bin
Baseline used for diff: workspace/iso-extract/ff7_d1_csr_base.bin

## BLOCKED: BLACKBGB.DAT

| Image | BLACKBGB |
|-------|----------|
| pristine | 13008 |
| CSR | 13013 (CSR-edited hub) |
| Clean noswap | 13009 |

CSR and Clean both edit BLACKBGB. Cannot paste Clean file onto CSR (would wipe CSR routing).
CSR still has Ask-for-disc candidate 0E 03 at file offset **432**.

### Operator (Makou) — required before calling pack complete

1. Open workspace/iso-extract/ff7_d1_csr_noswap_work.bin in Makou Reactor
2. Field **blackbgb** — remove all **Ask for disc** (keep jumps / gate bits)
3. Save FIELD into the same work bin
4. Rebuild layer vs CSR base (not pristine Clean) with bin_diff_to_layer:
   - base: workspace/iso-extract/ff7_d1_csr_base.bin
   - work: workspace/iso-extract/ff7_d1_csr_noswap_work.bin
   - out: builder/no-disc-swap-on-csr-v0.1.1/layers/disc1.layer.json
   - layer_id: no-disc-swap-on-csr-v0.1.1-disc1

## CSR+ stacking

CSR+ scene packs checked do **not** touch noswap maps on D1 (aerith-house).
cota/hojo/endgame are disc2/disc3 layers only.

Stack: **csr-v0.14.1** + CSR+ scenes + **no-disc-swap-on-csr-v0.1.1**

## Not in this pack

- manip-movie D2/D3 copies (deferred)
- Highwind pack (next)

## Verify after BLACKBGB fix

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base csr-v0.14.1 \
      --addon no-disc-swap-on-csr-v0.1.1
