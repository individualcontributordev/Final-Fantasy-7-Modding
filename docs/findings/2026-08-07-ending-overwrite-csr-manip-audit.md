# Ending LBA alias vs CSR manip-movies

**Date:** 2026-08-07  
**Image:** ending v7 (CD-sized) after LAST4_3 restore

## CSR manip seed (must keep)

| Seed | D1 home | Overlap ENDING*? | v7 status |
|------|---------|------------------|-----------|
| CANONON body | JAIROFAL @ 318357 | No | **OK** |
| CANONON absolute | LBA **250450** | Inside ENDING2E | **OK** (re-punched) |
| CANONHT2 | CAR_1209 @ 284833 | No | **OK** |
| LASTMAP.BIN | JAIROFLY @ 325716 | No | **OK** |
| LAST4_3.BIN | GOLD7_2 @ 264311 | **Yes (ENDING2E)** | **Restored** after alias |

## D1 movies under ending LBA ranges (collateral)

Fully or partly overwritten by D3 ending streams (not manip seeds except GOLD7_2):

ONTRAIN, MAINPLR, SMK, SOUTHMK, PLREXP, FALLPL, MONITOR, BIKEGET,
NVLMK, NIVLSFS, JENOVA_E, JUNON, HIWIND0, MTCRL, GOLD1, BISKDEAD,
BOOGDEMO, BOOGSTAR, SETO, RCKTFAIL, GOLD7, GOLD7_2, EARITHDD (part).

These are stock D1 mid-game FMVs. CSR single-disc already trades several
(e.g. RCKTFAIL tail for CANONON@250450). Not required by current manip seed.

## Rebuild step

`build_ending_credits_test_bin.py` step 5 rewrites GOLD7_2 = D3 LAST4_3
after ending + CANONON punches.
