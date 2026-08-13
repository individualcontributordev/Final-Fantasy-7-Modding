# INSTRUCTIONS — rebuild Disc 1 (Single-disc v0.1.29 break gate bit)

## Why

Disc 1→2 went straight into LOST2 (#634) with no break scene and no music.
Root cause: LOST2 only jumps to COS_BTM2 (#526) when bank3[0x84] bit4 is ON
and GM==0xa455. LOSIN2 clears that bit; nothing on BLACKBGB set it back.
v0.1.28 force blacked the break — this build sets the bit properly.

## Build

1. Hard-refresh builder (badge **v0.1.29**)
2. CSR + Single-disc only (CSR+ off)
3. APPLIED must include:
   - movies v0.1.4
   - single-disc-on-csr-v0.1.24
   - v0.1.26, v0.1.27, v0.1.28, **v0.1.29**
4. New Disc 1 zip; open the .cue

## Test

| Spot | Expect |
|------|--------|
| Disc 1→2 transition | **Break scene (COS_BTM2 #526)** first — not straight forest #634 |
| After break / LOST2 | Music present |
| PARASHOT #731 / #71 / #255 | Still OK |

## Evidence

- APPLIED.txt with **v0.1.29**
- Pass/fail break scene + music
