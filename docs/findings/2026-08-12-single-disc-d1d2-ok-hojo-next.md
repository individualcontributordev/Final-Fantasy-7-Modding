# Finding: D1 to D2 break OK on v0.1.9; Hojo / D3 path next

**Date:** 2026-08-12
**Status:** D1-D2 closed OK; Hojo open
**Stack:** CSR + single-disc-on-csr-v0.1.9

## Confirmed OK (human)

- Jenova fight
- End of disc 1 trims
- Transition to disc 2
- Break scene

## Open

Disc 2 Hojo fight glitched. After Hojo is disc 3 swap / transition.

## Byte notes

Post-Hojo path: CANON_2 to BLACKBGD (#105) to BLACKBGB (#103) to LAS0_1 (#744).

CANON_2 on SD vs CSR D2: all script slots equal, texts equal, AKAO size equal
but AKAO bytes differ; file hash OTHER. No DSKCG/ASK left in key MAPJUMP path
for hojyo/31.

CANONHT2/CANONON not present as MOVIE filenames on D1; seed/alias only via
manip-movies pack. CSR+ Hojo trim has disc1 layer and changes CANON_2 heavily.

## Next

Isolate H1 (SD only + movies) vs H2 (+ CSR+ Hojo). See docs/INSTRUCTIONS.md.
