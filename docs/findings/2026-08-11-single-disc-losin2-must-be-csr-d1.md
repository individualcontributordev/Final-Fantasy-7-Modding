# Finding: LOSIN2 (#632) must stay CSR D1 on single-disc

**Date:** 2026-08-11
**Status:** fixed in single-disc-on-csr-v0.1.9
**Report:** field 632 using disc 2; no break; black + regular disc 2 music

## Role of LOSIN2

Makou id 632 = losin2 = end of CSR disc 1 path, immediately before BLACKBGB
(#103) disc-change / break hub.

## Multi-disc CSR chain (working)

1. LOSIN2 (CSR D1) init when GM==0x2a2:
   - SETWORD GameMoment = 0x2a5
   - SETWORD GameMoment = 0xa455   ← break sentinel
2. cloud/3 MAPJUMP BLACKBGB
3. BLACKBGB: SETBYTE disc=2, DSKCG 2, MAPJUMP LOST2
4. LOST2 (CSR D2) / COS_BTM2: IFUW GM==0xa455 opens break choreography

## Single-disc bug

D2 FIELD merge replaced LOSIN2 with CSR Disc 2 bytes. D2 LOSIN2:

- Does not write 0xa455
- Still MAPJUMPs BLACKBGB with music

BLACKBGB (Ask-stripped) still jumps LOST2, but LOST2 and COS_BTM2 gates on
0xa455 stay false → skip break → black + D2-style music.

Confirmed hashes (v0.1.8):

| File | CSR D1 | CSR D2 | SD 0.1.8 |
|------|--------|--------|----------|
| LOSIN2 | A | B | B (wrong) |
| LOST2 | D1 variant | D2 | D2 (wanted for open) |
| COS_BTM2 | … | D2 | D2 |

## Fix

Restore CSR D1 LOSIN2 on the single-disc image. Keep D2 LOST2 + COS_BTM2.
Prefer list: LOSIN2.DAT d1 so future merges do not re-clobber.

## Rule

End-of-D1 maps that arm break/disc-transition state must prefer CSR D1.
Do not blindly install D2 for every field id >= 632.
