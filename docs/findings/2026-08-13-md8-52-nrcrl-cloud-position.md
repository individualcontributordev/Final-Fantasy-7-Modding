# Finding: CSR+single-disc MD8_52 Cloud-position FMV missing

**Compare:** CSR Disc 2 multi vs CSR + single-disc Disc 1.
**Symptom:** On CSR a movie plays that leaves Cloud in the correct place; on single-disc the movie is cut/broken or skipped.

## Maps

| Id | Field | Role |
|---:|-------|------|
| 731 | MD8_5 | DW approach; PMVIE mid=53 NRCRLB (fixed v0.1.21) |
| 779 | MD8_52 | Follow-up; PMVIE mid=52 NRCRL then MAPJUMP #72 FSHIP_25 |

## Root cause

1. Field: single-disc movie-trim removed PMVIE+MOVIE from MD8_52 dir3/0 (audit pairs 1 to 0) because D1 mid52 resolved to wrong MTNVL2.STR.
2. Script still MAPJUMP to FSHIP_25 without the FMV that positions the party/Cloud on CSR D2.

## Fix (v0.1.22)

- Restore CSR MD8_52.DAT (identical CSR D1/D2 scripts with Set+Play).
- Inject pristine D2 NRCRL.MOV into D1 movie id 52 (MTNVL2.STR slot; grew ISO).
- MOVIE_ID Form2 eng size/aux from source.

## Not changed

LOSIN2, LOST2, CANON_2, BLACKBGB, WHITE2, MD8_5 NRCRLB mid53.
