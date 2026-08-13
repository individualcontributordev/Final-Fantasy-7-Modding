# INSTRUCTIONS — rebuild Disc 1 (single-disc v0.1.24 + path-engine v0.1.25)

## Why

MD8_5 (#731) was glitched because D2 field scripts use engine movie IDs, and the
D1 MOVIE_ID table was too short / wrong. Fields 71 and 255 need CSR Disc 2 trims.

v0.1.25 is a small pack that auto-stacks on Single-disc v0.1.24.

## Build

1. Hard-refresh https://individualcontributor.dev/builder/
2. Base: CSR
3. Enable Single-disc (v0.1.24). Path-engine v0.1.25 should auto-include
4. CSR+ off for this check
5. APPLIED must list (in order):
   - single-disc-csr-manip-movies-v0.1.4
   - single-disc-on-csr-v0.1.24
   - single-disc-on-csr-v0.1.25
6. Build Disc 1

## Test

| Spot | Expect |
|------|--------|
| FSHIP_12 then MD8_5 (#731) | Full PARASHOT; field not glitched |
| FSHIP_24 (#71) | CSR D2 short trim (not long pristine) |
| BLIN66_6 (#255) | CSR D2 trim |
| Optional | Hojo / break / waterfall still OK |

## Evidence

- APPLIED.txt from zip
- Pass/fail PARASHOT on #731 and trims on #71/#255
