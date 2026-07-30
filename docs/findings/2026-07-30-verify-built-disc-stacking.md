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

Windows evidence in docs/windows-last-task.md; offset analysis vs CSR highwind + Modding field layer JSON; verifier updates 0cfcd6c / 19fcd32.

## Why it matters

Stops false FAIL on valid builder zips. Always pass **matching** base/addon ids from the zip folder name / APPLIED.txt.

## Infer config (no manual --addon)

`verify_built_disc.py` resolves disc/base/addons when flags are omitted:

1. **CLI** `--disc` / `--base` / `--addon` (if given, wins)
2. **Builder stamp** in `.bin` or parent folder name:
   `ff7-builder-d1+highwind-v0.1.1+field-encounter-on-highwind-25-v0.1.2+…`
3. **APPLIED.txt** next to the `.bin`: maps `Base:` / `Add-ons:` display names to catalog ids via local manifests

Prefer pointing the script at the **extract folder** (or the stamped `.bin` with APPLIED beside it). Wrong clean-vs-on-highwind ids from hand-typing should no longer happen.

## Follow-ups

- [x] EDC ignore in verify_built_disc
- [x] Addon-overwrite ignore for base check
- [x] Infer pack ids from stamp + APPLIED.txt
- [ ] Optional: CSR+ scene packs on CSR base (next matrix row)

## Sources

- scripts/verify_built_disc.py
- builder/edc.js (site)
- docs/07-hardware-burn.md (EDC repair note)
