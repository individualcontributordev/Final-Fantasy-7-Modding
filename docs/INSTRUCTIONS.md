# INSTRUCTIONS — playtest single-disc v0.1.21 (MD8_5 / 71-67-731)

## What changed

CSR Highwind path without scene skip: field 71 (FSHIP_24) to 67 (FSHIP_12) to 731 (MD8_5)
could hang after leaving the deck.

Cause: MD8_5 plays movie id 53. On Disc 2 that is NRCRLB; on Disc 1 it was still NIVLSFS.
Wrong FMV blocked progress after the MAPJUMP (jump itself was fine).

Fix: single-disc-on-csr-v0.1.21 injects D2 NRCRLB into D1 mid53.
Prior Hojo/break/waterfall field fixes unchanged.

## COPY-PASTE — rebuild + play

1. Hard-refresh https://individualcontributor.dev/builder/
2. Base: CSR
3. Add-on: Single-disc only (CSR+ scenes off)
4. Confirm APPLIED includes:
   - single-disc-on-csr-v0.1.21 (not 0.1.20)
   - single-disc-csr-manip-movies-v0.1.4 (auto)
5. Build Disc 1 zip and load in DuckStation.

## What to test

| Path | Expect |
|------|--------|
| No-skip Highwind / DW approach | 71 to 67 deck leave to 731 MD8_5 FMV then continue |
| Hojo CANON_2 + FMV audio | Still good (unchanged) |
| Disc 1 to 2 break (LOSIN2/LOST2) | Still good |
| Waterfall / LOSLAKE1 | Still good |

## If 731 still fails

Note whether MD8_5 loads (field art) vs black vs movie hang.
