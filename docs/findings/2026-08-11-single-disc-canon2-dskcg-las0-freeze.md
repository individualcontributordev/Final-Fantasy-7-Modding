# Finding: Post-Hojo freeze on field 744 (LAS0_1) — CANON_2 Ask disc 3

**Date:** 2026-08-11
**Status:** fix shipped in single-disc-on-csr-v0.1.5
**Stack:** CSR + CSR+ + Single-disc Disc 1
**Report:** After Hojo, transition to disc 3 freezes on field **744 = las0_1**.

## Map path

Hojo corridor uses CSR Disc 2 scripts on single-disc:

- BLIN66_6 / FSHIP_24 to **CANON_2 (#741)**
- CANON_2 to **blackbgd (#105)** to **blackbgb (#103)** to **las0_1 (#744)**

LAS0_1.DAT itself is byte-identical to CSR D1/D2/D3 (not a bad map).

## Root cause

Single-disc merge took **CSR D2 CANON_2**, which still has live **Ask for disc 3**
(DSKCG opcode, disc=3) in the end-of-scene script. Earlier single-disc work only
stripped Ask on **blackbgb / blackbge / blackbg3**, not on Sister Ray / CANON_2.

On a Disc 1-only image that Ask still runs the disc-change path and softlocks after the
fight when the game tries to move into Northern Cave (744).

Also found residual DSKCG 2/3 on a few other maps (COSMIN2, FRCYO, HYOU11, MDS5_W,
SHPIN_3, SUBIN_1B, WHITEBG3). HYOU8_1 still has one disc-2 Ask (compress grew past
ISO sector slot — left for later).

## Fix (v0.1.5)

NOP residual DSKCG disc 2/3 to size-preserving JMPF +0 on the maps that fit,
including **CANON_2**. CSR+ Hojo disc1 layer does not reintroduce those ops after the
strip.

## Verify locally

CANON_2 DSKCG2/3 empty after SD 0.1.5 (+ CSR+ hojo). LAS0_1 unchanged vs prior.
