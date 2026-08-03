# Finding: Supernova needs BATTLE.X LBA remap (not just SNOVA files)

**Date:** 2026-08-03
**Status:** v3 DuckStation PASS (Supernova completes)

## Failures

| Ver | Method | DS result |
|-----|--------|-----------|
| v1 | user-data inject, zero EDC | SFX + battle freeze |
| v2 | raw-copy SNOVA EDC intact | same freeze |

## Root cause

BATTLE.X.dec (gzipps) contains absolute Mode2 LBAs for D3 SNOVA assets:

- 0x48D78 + 8*n : SNOVA0..SNOVA15 as (lba, padded_size) pairs
- 0x4F5A8 : LASBOSS3.BIN (lba, padded_size 313344)

D3 values e.g. SNOVA0=127254, LASBOSS3=127101. No CdSearchFile path — pure LBA table.

Copying files to end of D1 leaves the table pointing at empty D3 sectors on the
D1 image → effect never completes.

## Fix v3

After raw-copy with LBA delta = new_snova_dir - 127100:

- rewrite each table lba to d3_lba + delta
- recompress BATTLE.X via compress_gzipps (fits under original size)
- replace_file_padded

Verified: all 17 table entries match find_file on patched image; no residual
127xxx LBAs left in BATTLE.X.

## Tool

mods/no-swap/scripts/inject_snova_d3_to_d1.py (v3)

## Playtest v3

**PASS (DuckStation):** Supernova effect completes; battle resumes.
Confirms BATTLE.X LBA remap + SNOVA file inject is sufficient for no-swap.

Console not yet tested.
