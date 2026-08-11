# Finding: CSR+ single-disc early freeze / glitch (layer apply order)

**Date:** 2026-08-11
**Status:** open — likely wrong apply order; builder fix shipped
**Stack:** CSR + CSR+ + Single-disc Disc 1
**Symptom:** graphics glitch on second field; softlock after elevator (music continues). Repro after DuckStation restart.

## Analysis

Early Midgar FIELD maps (NMKIN_*, MDS7*, ELEVTR1, ELM*) are byte-identical between
CSR-only and CSR+Single-disc+CSR+ except files CSR+ intentionally edits (late game).

CSR+ disc1 layers (Hojo/COTA/endgame) were bin-diffed against baseline:

  pristine D1 + CSR D1 + single-disc-on-csr

They are absolute image offsets. If the builder applies CSR+ packs before
Single-disc, those writes land on a different image layout and corrupt random
sectors. Field glitches + softlocks with music still playing fit corrupt field data.

## Builder fix

sortAddonsForApply: Single-disc core first, then movies/endings/gameplay mods,
then CSR+ scene packs last.

## Operator

Hard-refresh builder, rebuild CSR+SD, fresh DS boot. If still broken, bisect CSR-only
vs CSR+SD (no CSR+) vs full stack; paste APPLIED.txt order.
