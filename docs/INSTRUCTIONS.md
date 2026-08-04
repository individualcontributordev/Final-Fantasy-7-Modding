# Task: No-disc-swap - CSR pack next (Clean retired)

## Policy (locked)

- CSR base: keeps certain FMVs for manips - D2/D3 movie pack **required** with no-disc-swap
- CSR+: removes field FMVs - no manip-movie pack
- Highwind: trims - no manip-movie pack
- Unmodified: no no-disc-swap

no-disc-swap only for:

- CSR
- CSR + CSR+ layers
- Highwind

Not for Unmodified/clean. Other mods on clean OK if they do not touch fields/FMVs
(e.g. encounter rate packs).

Clean pack disabled in builder manifest.

Finding: docs/findings/2026-08-04-noswap-bases-csr-highwind-only.md

## Next work

Build no-disc-swap-on-csr-v0.1.1 (or next version):

1. CSR baseline D1 image
2. Makou Ask + movie trims on CSR FIELD
3. SNOVA + BATTLE.X inject (always with no-disc-swap)
4. Layer vs CSR baseline; compatibleBases live csr-v*
5. CSR-base manip-movies pack (required with CSR no-disc-swap)
6. Highwind pack later

## After Pages deploy

Confirm Clean no-disc-swap no longer listed; encounter mods still on clean.

## Evidence

    Clean pack hidden: yes/no
    CSR pack:

Say check.
