# Finding: Rename no-disc-swap → single-disc

**Date:** 2026-08-04
**Status:** done in repo

## Decision

Internal and builder identifiers use **single-disc** (not no-disc-swap).

| Old | New |
|-----|-----|
| mods/no-disc-swap | mods/single-disc |
| no-disc-swap-on-csr-v* | single-disc-on-csr-v* |
| no-disc-swap-clean-v* | single-disc-clean-v* |
| exclusiveGroup no-disc-swap | single-disc |
| findings *noswap* | *single-disc* |

UI label: Single-disc play (optional). Tech unchanged (Ask trims, movie trims, SNOVA).
