# Finding: no-disc-swap bases - CSR / CSR+ / Highwind only (not Clean)

**Date:** 2026-08-04
**Status:** product decision (operator)

## Decision

no-disc-swap may be applied only to:

- CSR base (keeps manip-critical FMVs)
- CSR + CSR+ scene stacks (CSR+ removes field FMVs; no movie-copy pack)
- Highwind base (cutscene trims; no movie-copy pack)

Unmodified (clean) is out of scope for no-disc-swap.

## Rationale

Unmodified should keep the spirit of a vanilla disc: players may stack mods that
do not alter field scripts or FMV routing (e.g. field/world encounter rate).
no-disc-swap changes Ask-for-disc, field movie ops, and battle SNOVA - too heavy
for unmodified.

## Builder

- no-disc-swap-clean-v0.1.1 (and any clean-only ids): enabled false + retired blurb
- Next packs: no-disc-swap-on-csr-v*, no-disc-swap-on-highwind-v*, optional
  no-disc-swap-csr-manip-movies-v*

## Related

- 2026-08-04-noswap-csr-manip-movies-pack-split.md
- mods/no-disc-swap/README.md
