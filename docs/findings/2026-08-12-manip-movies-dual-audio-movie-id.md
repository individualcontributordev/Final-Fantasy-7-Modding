# Finding: manip-movies dual/flicker audio — wrong MOVIE_ID eng size

**Date:** 2026-08-12
**Status:** fix shipped single-disc-csr-manip-movies-v0.1.3
**Report:** After CANON_2 OK, manip-movies sound broken: real audio + flickering extra

## Cause

Seed inject put CSR D2 CANONHT2 bytes into D1 CAR_1209.STR (payload match).
MOVIE_ID row kept:

- eng_size = ISO byte size (5240832)
- aux from old D1 CAR row

CSR D2 CANONHT2 row uses:

- eng_size = nsec * 2336 (5977824) Form2 engine length
- source aux (b/c)

Mismatch lets the player run wrong length/metadata vs residual old CAR XA in
the abandoned tail after shrink. Result: dual/flicker audio.

## Fix

inject_movies_by_disc_id.py: always patch MOVIE_ID from source Form2 meta;
if eng_size smaller than form2 estimate, force nsec*2336. Optional residual
zero via FF7_ZERO_MOVIE_RESIDUAL=1 (huge layer).

Pack: single-disc-csr-manip-movies-v0.1.3
