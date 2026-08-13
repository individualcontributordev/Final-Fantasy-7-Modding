# INSTRUCTIONS — rebuild Disc 1 (Single-disc v0.1.28 break scene)

## Why

Disc 1→2 went straight into LOST2 (#634) with no break scene and no music.
Break must play **COS_BTM2 (#526)** first (CSR multi-disc path). That MAPJUMP
was skipped because pure CSR D2 LOST2 still had the IFUW else +0x0B skip.

## Build

1. Hard-refresh builder
2. CSR + Single-disc only (badge v0.1.28)
3. APPLIED must include:
   - movies v0.1.4
   - single-disc-on-csr-v0.1.24
   - v0.1.26, v0.1.27, **v0.1.28**
4. New Disc 1 zip; open the .cue

## Test

| Spot | Expect |
|------|--------|
| Disc 1→2 transition | **Break scene (COS_BTM2)**, not straight into forest #634 |
| After break / LOST2 | Music present |
| PARASHOT #731 / #71 / #255 | Still OK |

## Evidence

- APPLIED.txt with v0.1.28
- Pass/fail break scene + music
