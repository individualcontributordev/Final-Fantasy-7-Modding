# Finding: FSHIP_12 (#67) to MD8_5 (#731) stuck on single-disc

**Stack:** csr-v0.14.1 + single-disc-on-csr (<=0.1.20) + manip-movies
**Report:** CSR Highwind scenes without skip: field 71 to 67 to 731; transition from 67 felt broken.

## Maplist

| Id | Stem | Role |
|---:|------|------|
| 71 | fship_24 | Highwind interior (CSR D2) |
| 67 | fship_12 | Deck; ASK leave party; MAPJUMP 731 |
| 731 | md8_5 | Diamond Weapon approach field |

## What is not broken

- FSHIP_24 to FSHIP_12 MAPJUMP exists on CSR D2 FSHIP_24 (SD has those bytes).
- FSHIP_12 ad/31 MAPJUMP to #731 is byte-identical CSR D1 = CSR D2 = SD 0.1.20.
- Script table after FSHIP_12 movie trims still points at valid ad/31 ASK+MAPJUMP.

## Root cause

MD8_5 dir/0 (same on CSR D1/D2/SD):

1. Fade / lock controls
2. PMVIE mid=53 + MOVIE
3. SETWORD GameMoment progress
4. Unlock

Movie id 53 is disc-local:

| Disc | Sorted MOVIE name at id 53 |
|------|----------------------------|
| D2 / CSR multi | NRCRLB.MOV (correct) |
| D1 / single-disc | NIVLSFS.MOV (wrong) |

Wrong Form2 stream can hang before SETWORD — looks like 67 to 731 broken.

## Fix

single-disc-on-csr-v0.1.21: inject pristine D2 NRCRLB.MOV into D1 slot NIVLSFS.MOV
(mid 53) with Form2 MOVIE_ID eng size/aux.

Side effect: BLACKBG4 debug hub mv/1 mid53 also gets NRCRLB — acceptable.

## Not changed

LOSIN2 d1, LOST2 d2, CANON_2 d2, BLACKBGB strip, WHITE2 hybrid, FSHIP FIELD trims.

## Verify

FIELD FSHIP_12/24/MD8_5/CANON_2/LOSIN2/LOST2/BLACKBGB identical vs 0.1.20 after inject;
only MOVIE/NIVLSFS + MOVIE_ID change.
