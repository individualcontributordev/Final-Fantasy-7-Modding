# Finding: single-disc bases - CSR / CSR+ / Highwind only (not Clean)

**Date:** 2026-08-04
**Status:** product decision (operator)

## Decision

**Ship first:** CSR+ stacks and Highwind. **Defer:** CSR base + manip movies (size).

single-disc may be applied only to:

- CSR base (later - manip movies required; disc space limited)
- CSR + CSR+ scene stacks (CSR+ removes field FMVs; no movie-copy pack)
- Highwind base (cutscene trims; no movie-copy pack)

Unmodified (clean) is out of scope for single-disc.

## Rationale

Unmodified should keep the spirit of a vanilla disc: players may stack mods that
do not alter field scripts or FMV routing (e.g. field/world encounter rate).
single-disc changes Ask-for-disc, field movie ops, and battle SNOVA - too heavy
for unmodified.

## Builder

- single-disc-clean-v0.1.1 (and any clean-only ids): enabled false + retired blurb
- Next packs: single-disc-on-csr-v* + single-disc-csr-manip-movies-v* (required pair on CSR base),
  single-disc-on-highwind-v*

## Related

- 2026-08-04-single-disc-csr-manip-movies-pack-split.md
- mods/single-disc/README.md
