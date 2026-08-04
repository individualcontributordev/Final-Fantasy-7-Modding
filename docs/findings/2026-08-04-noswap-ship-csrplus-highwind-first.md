# Finding: Ship no-disc-swap for CSR+ and Highwind first; defer CSR base

**Date:** 2026-08-04
**Status:** product decision (operator)

## Decision

Implement and publish no-disc-swap first for:

1. **CSR + CSR+ scene packs**
2. **Highwind**

Defer:

- **CSR base alone** + manip-critical D2/D3 movie copies on D1

## Why

CSR base keeps manip FMVs, so single-disc needs a movie whitelist on D1. After SNOVA,
D1 only has ~93 MB free on an 80-min CD - full/large FMV sets do not fit. CSR+ and
Highwind remove or skip field FMVs, so core pack (Ask trims + crawl Set/Play trims +
SNOVA/BATTLE.X) is enough without growing the disc further.

## Stacks when shipping this phase

| Config | Base | Add-ons |
|--------|------|---------|
| CSR+ single disc | CSR | CSR+ scene packs + no-disc-swap-on-csr |
| Highwind single disc | Highwind | no-disc-swap-on-highwind |

No manip-movies pack in this phase.

## Later

CSR base + no-disc-swap-on-csr + no-disc-swap-csr-manip-movies (tight whitelist under ~90 MB raw).

## Related

- 2026-08-04-noswap-bases-csr-highwind-only.md
- 2026-08-04-noswap-csr-manip-movies-pack-split.md
