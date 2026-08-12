# Finding: CANON_2 glitch on load — DSKCG strip hit AKAO

**Date:** 2026-08-12
**Status:** fixed in single-disc-on-csr-v0.1.20
**Stack:** CSR + Single-disc only (CSR+ off); field glitched when CANON_2 loads

## Symptom

Hojo field (#741 CANON_2) fully glitched on load. Disc-3 transition not testable.

## Not the cause

- MIM/BSX: identical to CSR D2
- Script slots / texts: identical to CSR D2
- Movies pack: does not change CANON_2.DAT
- Real DSKCG/ASK opcodes on CSR D2 CANON_2: **none**

## Cause

v0.1.5 era residual Ask strip turned seven AKAO payloads of `0e 03` into `10 00`
(JMPF +0 style / DSKCG nop pattern) without parsing opcodes. Same compressed
size ±; 14 bytes differ, all inside AKAO.

CSR D2 AKAO contains 37x `0e 03`; SD had 30x `0e 03` + 7 corrupted pairs.

## Fix

Restore byte-identical CSR Disc 2 FIELD/CANON_2.DAT on the single-disc image.

## Lesson

Never bulk-replace 0x0E / 0x0E0x patterns in full decompressed FIELD blobs.
Only patch confirmed DSKCG/ASK ops from the script decoder.
