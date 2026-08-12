# Finding: CSR+single-disc missing PARASHOT on FSHIP_12

**Compare:** CSR Disc 2 multi vs CSR + single-disc.
**User:** the movie is called PARASHOT (positions Cloud).

## Path

| Id | Field | CSR D2 |
|---:|-------|--------|
| 67 | FSHIP_12 | ad/3 PMVIE **59 PARASHOT**, **50 METEOFIX**, **51 METEOSKY** then MAPJUMP |
| 779 | MD8_52 | NRCRL then FSHIP_25 (fixed v0.1.22) |
| 731 | MD8_5 | NRCRLB (fixed v0.1.21) |

## Root cause

Single-disc movie-trim removed FSHIP_12 Set+Play. D1 mid59 was OPENINGE not PARASHOT.
Same script block needs mid50/51 (METEOFIX/METEOSKY) for the full CSR deck FMV sequence.

## Fix (v0.1.23)

- Restore CSR FSHIP_12.DAT.
- Inject D2 PARASHOT -> D1 OPENINGE (mid59); METEOFIX->MTCRL; METEOSKY->MTNVL.
