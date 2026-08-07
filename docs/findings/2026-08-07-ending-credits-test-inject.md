# Ending credits test inject

**Date:** 2026-08-07  
**Status:** v5 — Form1 camera id23 + no early MOVIE; Form2 24+

## Pointer model

- **PMVIE n** → `MINT/MOVIE_ID.BIN` **row n** (not ISO name sort).
- Form2 engine size ≈ `sectors * 2336` + source a/b/c.
- Some rows are **Form1 `.BIN`** (camera / non-MDEC). Aux often  
  `b=0x00e00140`, high `c` (`0x200xx`). **Must not** be MDEC-played.

| id | Disc 3 | Form | Role |
|---:|--------|------|------|
| 23 | LASTMAP.BIN | Form1 | camera preset |
| 24 | LASTFLOR.MOV | Form2 | LASTMAP final FMV |
| 25 | ENDING01.MOV | Form2 | LAS4_0 |
| 26 | ENDING3E.MOV | Form2 | ending |
| 29 | ENDING2E.MOV | Form2 | long credits |

## Failure ladder

| Ver | Failure | Cause |
|-----|---------|--------|
| v0 | black / random | field stripped MOVIE ops |
| v2 | freeze | MOVIE_ID size 2048× not 2336× |
| v3 | MDEC crash | Form1 LASTMAP.BIN fed as FMV |
| v4 | MDEC crash @ ONTRAIN LBA | id23 left as FMV; AD MOVIE still plays id23 |
| v5 | (test) | id23=D3 BIN; AD S31 MOVIE nop; FMV via PMVIE24+AD3 MOVIE |

## v5 artifacts

- `mods/single-disc/patches/ending-lastmap-v5.DAT` — pristine LASTMAP LZS  
  with AD S31 `F9`→`00` (surgical compress byte).  
- Manifest injects LASTMAP.BIN + LASTFLOR + ENDING01/3E/2E.  
- Builder: `build_ending_credits_test_bin.py`

## Play

```text
workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

~1008274176 bytes. DuckStation only. Not in builder packs.
