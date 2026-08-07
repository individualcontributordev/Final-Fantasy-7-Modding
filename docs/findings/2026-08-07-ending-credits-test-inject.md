# Ending credits test inject

**Date:** 2026-08-07  
**Status:** v4 — Form2 streams only; no LASTMAP.BIN

## Pointer model (confirmed)

- Field **PMVIE n** → `MINT/MOVIE_ID.BIN` **row n** (20-byte records).
- Row is **not** ISO `MOVIE/` alphabetical index (that mismatches on every disc).
- D1 and D3 share the same early row layout for ending ids; D3 has fewer total rows.
- Engine **size** for Form2 is usually `sectors * 2336`, plus aux a/b/c from source disc.

| id | Disc 3 file | Sector form |
|---:|-------------|-------------|
| 23 | LASTMAP.BIN | **Form1** (submode 0x08) — **not** playable as FMV |
| 24 | LASTFLOR.MOV | Form2 |
| 25 | ENDING01.MOV | Form2 |
| 26 | ENDING3E.MOV | Form2 |
| 29 | ENDING2E.MOV | Form2 |

## Failure ladder

| Ver | Symptom | Root cause |
|-----|---------|------------|
| v0 | Random clip / black | Single-disc stripped LASTMAP/LAS4_0 MOVIE ops |
| v2 | LASTMAP freeze | MOVIE_ID size = ISO 2048×sec, not D3 2336×sec |
| v3 | MDEC invalid + null fault | Injected **LASTMAP.BIN** into id 23; first `MOVIE` plays Form1 as MDEC |
| v4 | (test) | Form2 only on 24/25/26/29; id 23 left as D1 ONTRAIN FMV |

## v4 build

1. Playtest base (CSR + main 0.1.2 + movies 0.1.2).  
2. Pristine FIELD/LASTMAP.DAT + LAS4_0.DAT.  
3. Manifest (no LASTMAP.BIN):

```text
3 LASTFLOR.MOV ->MAINPLR.MOV
3 ENDING01.MOV ->SMK.STR
3 ENDING3E.MOV ->SOUTHMK.MOV
3 ENDING2E.MOV ->MONITOR.STR
```

Tool copies D3 MOVIE_ID size/aux; keeps grown D1 LBA.

```bash
python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
# workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

Size **1008274176**. DuckStation only.

## Note on single-disc core

Ship pack **zeros** LASTMAP AD PMVIE/MOVIE (avoids missing D3 streams).  
This test restores them on purpose.

## Caveats

- Id 23 may flash ONTRAIN once before LASTFLOR if the early PMVIE 23 path runs.
- Not CD-sized; not in builder packs.
