# verify_built_disc stacking rules (EDC + addon overwrites)

**Date:** 2026-07-30  
**Confidence:** confirmed  
**Status:** promoted  
**Related:** [world-light-runtime-verify](2026-07-30-world-light-runtime-verify.md), scripts/verify_built_disc.py, site builder/edc.js

## Summary

When verifying a **builder zip** (base + addons already stacked), do not require the image to match the base layer on every byte. Builder repairs Mode2 EDC/ECC after apply; addons intentionally overwrite base user data (e.g. FIELD.BIN stub on Highwind). Matching must use the **same pack ids as APPLIED**, ignore EDC/ECC, and ignore base user-bytes covered by later addons.

## Context

Highwind + on-highwind Light field/world zip was correct (APPLIED + stubs YES) but verify failed twice: (1) clean pack ids used by mistake; (2) base MISSING at EDC offset then at FIELD bytes overwritten by field addon.

## Discovery

### Correct Highwind Light config (disc 1)

- `--base highwind-v0.1.1`
- `--addon field-encounter-on-highwind-25-v0.1.2`
- `--addon world-encounter-on-highwind-25-v0.1.0`

Not clean `field-encounter-25-v0.1.2` / `world-encounter-25-v0.1.0` (compatibleBases clean only).

### EDC/ECC

- Mode2/2352 user data ends before sector offset **2072**; EDC/ECC follow.
- Site builder regenerates EDC/ECC on changed sectors after layers.
- Layer JSON may still contain EDC/ECC record bytes from the base diff.
- **verify_built_disc** compares only bytes with `abs_off % 2352 < 2072`.

### Addon overwrites base

- Example fail offset `0x7b5e0a9` (sector_off 41): covered by Highwind disc1 layer and field-encounter-on-highwind Light.
- Final image must match **addon** there, not pure Highwind.
- **verify_built_disc** collects addon user offsets first, then base check uses `ignore_user_offsets`.

### Published-pack matrix (playtest)

| Base | Field Light | World Light | Verify + play |
|------|-------------|-------------|---------------|
| clean | field-encounter-25 | world-encounter-25 | PASS |
| csr-v0.14.1 | on-csr-25 | on-csr-25 | PASS (human) |
| highwind-v0.1.1 | on-highwind-25 | on-highwind-25 | PASS script + human play OK |

## How we found it

Operational evidence in docs/INSTRUCTIONS.md; offset analysis vs CSR highwind + Modding field layer JSON; verifier updates 0cfcd6c / 19fcd32.

## Why it matters

Stops false FAIL on valid builder zips. Always pass **matching** base/addon ids from the zip folder name / APPLIED.txt.

## Config source: APPLIED.txt only

`verify_built_disc.py` takes a path to the built `.bin` or extract folder and reads
**only** `APPLIED.txt` beside the image:

- `Disc: N`
- `Base: …` → catalog base id (or clean for Unmodified/retail)
- `Add-ons:` list → catalog addon ids via display `name` match

No `--disc` / `--base` / `--addon`. Missing APPLIED or unmapped lines → hard fail.
Point at the builder zip extract so APPLIED stays next to the `.bin`.

## Follow-ups

- [x] EDC ignore in verify_built_disc
- [x] Addon-overwrite ignore for base check
- [x] Config exclusively from APPLIED.txt
- [ ] Optional: CSR+ scene packs on CSR base (next matrix row)

## Sources

- scripts/verify_built_disc.py
- builder/edc.js (site)
- docs/07-hardware-burn.md (EDC repair note)
