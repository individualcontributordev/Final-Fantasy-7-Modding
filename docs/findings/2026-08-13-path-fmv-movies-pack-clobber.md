# Path FMV clobber by manip-movies pack

## Symptom

PARASHOT does not play; field 731 (MD8_5) glitched on CSR+single-disc with auto movies.

## Cause

Apply order was SD core then manip-movies. Movies pack grew JAIROFAL/CANONON and
rewrote MOVIE_ID/shared LBAs over path injects (NRCRL mid52 shared JAIROFAL LBA;
METEOFIX/METEOSKY clobbered).

## Fix

1. Builder addonApplyRank: movies=10, single-disc-on-csr=20.
2. v0.1.24 layer vs CSR+movies baseline; inject_one(..., force_append=True).
