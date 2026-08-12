# INSTRUCTIONS — playtest single-disc v0.1.22 (MD8_52 Cloud FMV)

## What changed

Vs CSR Disc 2 multi: after Diamond Weapon approach, MD8_52 should play NRCRL
(positions Cloud) then Highwind FSHIP_25.

Single-disc had removed that Set+Play; jump still happened so the movie felt cut/broken.

v0.1.22: restore MD8_52 movie ops + inject D2 NRCRL at mid52.
MD8_5 NRCRLB (v0.1.21) kept. Hojo/break untouched.

## Build

1. Hard-refresh https://individualcontributor.dev/builder/
2. Base CSR, Single-disc only (CSR+ off)
3. APPLIED must include single-disc-on-csr-v0.1.22 (+ manip-movies + endings auto)
4. Build Disc 1

## Test

| Path | Expect |
|------|--------|
| DW Highwind path (no skip) | MD8_5 FMV, then MD8_52 NRCRL plays fully, Cloud ends correct, to FSHIP_25 |
| CSR D2 multi compare | Same movie/exit as multi-disc CSR |
| Hojo / disc1 to 2 break / waterfall | Still OK |
