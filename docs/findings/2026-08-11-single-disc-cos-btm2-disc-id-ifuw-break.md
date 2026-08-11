# Finding: Single-disc disc1-to-disc2 black+music — COS_BTM2 disc-id IFUW

**Date:** 2026-08-11
**Status:** fix shipped in single-disc-on-csr-v0.1.7
**Stack:** CSR + Single-disc (no CSR+) — Build C confirmed fail

## Confirmed

| Build | Disc1 to disc2 break |
|-------|----------------------|
| CSR multi-disc (swap D2) | OK |
| CSR + Single-disc only (movies pack on) | **black + music, no break** |
| CSR + CSR+ + Single-disc | same fail |

## Path

1. BLACKBGB to MAPJUMP lost2 (Ask stripped)
2. LOST2 init: v0.1.6 forces IFUW so MAPJUMP cos_btm2 always runs
3. COS_BTM2 directr/timeout: break sits behind IFUW disc-id gate

On multi-disc, after DSKCG disc swap the gate is true and break plays.
On single-disc disc id stays 1 so the else jump skips to music only.

## Fix (v0.1.7)

Clear COS_BTM2 IFUW else-jumps when else is at least 0x08.
Tool: mods/single-disc/scripts/force_cos_btm2_break_ifuw.py

## Note

Build C failed with movies pack on, so COS_BTM2 gate is the primary skip.
