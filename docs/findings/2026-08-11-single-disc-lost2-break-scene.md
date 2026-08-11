# Finding: Disc1→disc2 freeze / missing LOST2 break scene

**Date:** 2026-08-11  
**Status:** fix shipped in single-disc-on-csr-v0.1.6  
**Stack:** CSR + CSR+ + Single-disc Disc 1  
**Report:** Transition disc 1→2 freezes on “disc 2”; no break scene at start of disc 2.

## Intended path

1. Hub **blackbgb (#103)** jumps to **lost2 (#634)** (Ask disc 2 removed on single-disc).
2. CSR **Disc 2 LOST2** init can **MAPJUMP cos_btm2 (#526)** — the CSR break/routing scene.
3. That MAPJUMP sits behind **IFUW @ script 1201** (`18 20 00 00 55 a4 00 0b`).

## Why single-disc missed the break

Single-disc already ships **CSR D2 LOST2** bytes (prefer list).  
On multi-disc, disc change / disc id / nearby flags make IFUW fall through to MAPJUMP **cos_btm2**.

On Disc 1-only, the same IFUW often **takes the else branch** (jump +0x0B) and **skips** the break MAPJUMP. Result: land on LOST2 forest without the D2 open break, and session can look frozen / glitched (save-state / long sessions made it worse).

Raw byte `0e 02` next to the MAPJUMP is the **field id 526**, not a residual DSKCG.

## Fix (v0.1.6)

In LOST2 script: IFUW @1201 else-jump **0x0B → 0x00** so control always reaches  
`MAPJUMP cos_btm2 (-133,-1508) tri 101`.

Includes all v0.1.5 residual Ask strips (CANON_2, etc.).

## Note

Cold DuckStation boot + in-game save still preferred for repro; pack fix targets skip of break MAPJUMP, not emulator-only pollution.
