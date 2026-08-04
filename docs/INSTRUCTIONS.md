# Task: No-disc-swap CSR — manip FMV strategy

## Question

CSR needs critical FMVs for manips. Can we copy those onto D1 only for CSR base,
and not when CSR+ layers are applied?

## Answer

Yes — with two builder add-ons (preferred), not a conditional inside one layer.

Builder layers only stack forward. CSR+ cannot strip movies a prior pack injected.

### Preferred split

1. no-disc-swap-on-csr — Asks, non-manip movie trims, SNOVA+BATTLE.X
2. no-disc-swap-csr-manip-movies (optional) — whitelist D2/D3 MOVIE inject for manips

| Stack | Enable |
|-------|--------|
| CSR + manips + single disc | CSR + no-disc-swap-on-csr + manip-movies |
| CSR + CSR+ scenes + single disc | CSR + CSR+ packs + no-disc-swap-on-csr (omit manip-movies) |

### Alternative

One fat CSR no-disc-swap that always includes manip movies — simpler; CSR+ burns larger.

### Not in Clean / Highwind

Manip movie copies are CSR-only. SNOVA stays on every no-disc-swap pack.

## Finding

docs/findings/2026-08-04-noswap-csr-manip-movies-pack-split.md

## Next when implementing CSR pack

1. Core no-disc-swap-on-csr first (SNOVA + asks + crawl trims)
2. Manip whitelist from CSR notes + failures
3. Movie inject + table plumbing
4. Optional second pack (or fat merge if whitelist tiny)

Say check when starting CSR implementation.
