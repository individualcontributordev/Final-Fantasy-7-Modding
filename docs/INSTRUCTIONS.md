# INSTRUCTIONS — single-disc v0.1.24 (PARASHOT + MD8_5)

## What broke

With CSR + single-disc + auto manip-movies, path FMVs (PARASHOT, NRCRL) were
written then overwritten by the movies pack (shared disc LBAs with JAIROFAL/etc).
Result: PARASHOT missing; MD8_5 mid53 stream/meta glitched.

## Fix v0.1.24

- Apply order: manip-movies first, then single-disc-on-csr.
- Single-disc pack rebuilds path FMVs at unique EOF LBAs after movies.
- FSHIP_12 plays PARASHOT (+ meteo); MD8_5 NRCRLB; MD8_52 NRCRL.

## Build

1. Hard-refresh builder
2. CSR + Single-disc only (CSR+ off)
3. APPLIED must show single-disc-on-csr-v0.1.24 and manip-movies v0.1.4
4. Build Disc 1

## Test

| Path | Expect |
|------|--------|
| FSHIP_12 | Full PARASHOT (Cloud position) |
| MD8_5 #731 | Clean NRCRLB FMV, field not glitched |
| MD8_52 | NRCRL then Highwind |
| Waterfall / Hojo / break | Still OK |
