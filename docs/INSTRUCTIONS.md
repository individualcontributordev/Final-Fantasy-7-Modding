# INSTRUCTIONS — playtest single-disc v0.1.23 (PARASHOT)

## What changed

CSR Disc 2 Highwind deck movie **PARASHOT** (FSHIP_12) was stripped on single-disc.
v0.1.23 restores FSHIP_12 Set+Play and injects D2 PARASHOT (+ METEOFIX/METEOSKY).
MD8_52 NRCRL / MD8_5 NRCRLB / Hojo / break still kept from prior ships.

## Build

1. Hard-refresh https://individualcontributor.dev/builder/
2. Base CSR, Single-disc only (CSR+ off)
3. APPLIED: **single-disc-on-csr-v0.1.23** (+ manip-movies + endings auto)
4. Build Disc 1

## Test

| Path | Expect |
|------|--------|
| Highwind deck / FSHIP_12 | **PARASHOT** plays fully (Cloud positioned) like CSR D2 |
| MD8_52 / MD8_5 | Still correct FMVs |
| Hojo / disc break / waterfall | Still OK |
