# Ending credits test inject (DuckStation oversize bin)

**Date:** 2026-08-07  
**Status:** v2 — field scripts restored + D3 streams on MOVIE_ID rows

## Why inject-only failed

1. Single-disc **LASTMAP.DAT** removed ending **MOVIE** / PMVIE setup (pristine has
   PMVIE 23, 24, and MOVIE). Result: no correct stream → garbage / black silence.
2. Single-disc **LAS4_0.DAT** inserts **JMPF** before PMVIE 25 + MOVIE.
3. PMVIE uses **MOVIE_ID.BIN row index**, not ISO name order.

## v2 fix (test bin only)

1. Base: normal playtest (CSR + main 0.1.2 + movies 0.1.2).
2. Restore **pristine** FIELD/LASTMAP.DAT and FIELD/LAS4_0.DAT.
3. Inject D3 files into D1 slots for MOVIE_ID ids:

| id | D3 source | D1 slot file |
|---:|-----------|--------------|
| 23 | LASTMAP.BIN | ONTRAIN.MOV |
| 24 | LASTFLOR.MOV | MAINPLR.MOV |
| 25 | ENDING01.MOV | SMK.STR (grew) |
| 26 | ENDING3E.MOV | SOUTHMK.MOV (grew) |
| 29 | ENDING2E.MOV | MONITOR.STR (grew) |

Manifest: `mods/single-disc/patches/ending-credits-test-manifest.txt`

Verified: D3 payload match; LASTMAP has PMVIE 23/24 + MOVIE; LAS4_0 has PMVIE 25 + MOVIE.

## Play

```text
workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

Size **1008274176** bytes — DuckStation only, not CD/builder.

## Caveats

Overwrites movie ids 23–26, 29; restores pristine last-map field scripts (drops
those single-disc trims on this test image only).
