# Finding: LOSLAKE1 waterfall played rocket town again (LBA 250450)

**Date:** 2026-08-12
**Status:** fixed manip-movies v0.1.4
**Stack:** CSR + single-disc-on-csr-v0.1.20 + movies (CSR+ off)

## Symptom

Bugen / Cosmo waterfall FD manip scene played rocket town FMV again
(same class as pre-v0.1.1/v0.1.2).

## Cause

LOSLAKE1 seeks ISO LBA 250450 (not only MOVIE_ID[47]).

| Disc | LBA 250450 |
|------|------------|
| CSR D2 | CANONON.MOV start (Form2) |
| Stock D1 / SD without alias | mid RCKTFAIL.MOV |

v0.1.3 inject put CANONON bytes in JAIROFAL + correct id47 MOVIE_ID, but did
not write sectors at 250450. Absolute seek still hit rocket.

## Fix

v0.1.4 = inject (Form2 MOVIE_ID) + alias_d2_seek_lba_on_d1.py (raw CANONON at
250450). RCKTFAIL tail clobbered (known tradeoff).

## Verify

sdm LBA250450 sector0 == CSR2 CANONON sector0; id47 eng Form2; JAIROFAL==CANONON.
