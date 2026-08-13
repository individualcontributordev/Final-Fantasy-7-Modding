# INSTRUCTIONS — rebuild Disc 1 (Single-disc v0.1.25)

## Why

One Single-disc checkbox. The path-engine fix (MOVIE_ID / fields 71+255) is
hidden and always auto-applied with it (GitHub layer size split).

## Build

1. Hard-refresh https://individualcontributor.dev/builder/
2. Base: CSR
3. Mods: **Single-disc** only — badge **v0.1.25**. Do not look for a second row.
4. CSR+ off for this check
5. APPLIED should list (order):
   - single-disc-csr-manip-movies-v0.1.4
   - single-disc-on-csr-v0.1.24
   - single-disc-on-csr-v0.1.25  (auto, not in checklist)
6. Build Disc 1

## Test

| Spot | Expect |
|------|--------|
| FSHIP_12 then MD8_5 (#731) | Full PARASHOT; field not glitched |
| FSHIP_24 (#71) | CSR D2 trim |
| BLIN66_6 (#255) | CSR D2 trim |

## Evidence

- APPLIED.txt
- Pass/fail for #731 / #71 / #255
