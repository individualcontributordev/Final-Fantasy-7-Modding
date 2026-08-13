# INSTRUCTIONS — rebuild Disc 1 (Single-disc v0.1.27 LOST2 music)

## Why

Field 634 LOST2 after the disc 1 to 2 break had no music. CSR D2 LOST2 does
AKAO2 resume-music before MUSIC; without DSKCG (Ask-stripped on single-disc)
that resume leaves silence.

## Build

1. Hard-refresh builder
2. CSR + Single-disc only (badge v0.1.27)
3. APPLIED must include (order):
   - single-disc-csr-manip-movies-v0.1.4
   - single-disc-on-csr-v0.1.24
   - single-disc-on-csr-v0.1.26
   - single-disc-on-csr-v0.1.27
4. Build Disc 1 (new zip)
5. Open the .cue

## Test

| Spot | Expect |
|------|--------|
| Disc break then LOST2 #634 | Music plays (not silent) |
| FSHIP_12 then MD8_5 #731 | PARASHOT still OK |
| FSHIP_24 #71 / BLIN66_6 #255 | CSR D2 trims |

## Evidence

- APPLIED.txt with v0.1.27
- Pass/fail music on #634
