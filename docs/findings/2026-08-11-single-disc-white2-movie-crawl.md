# Finding: WHITE2 (field 643) crawl — movie pairs, not hybrid DAT

**Date:** 2026-08-11  
**Status:** fix shipped in single-disc-on-csr-v0.1.4  
**Report:** After v0.1.3, field **643 WHITE2** slowed down with graphical glitches.

## DuckStation log signature

```
W(DMARead): Insufficient data in output FIFO (requested 32, have 8)
D/MDEC: Invalid MDEC command 0x8A010160 / 0x0FFF1000 / …
V/PerfMon: FPS: 0.00 … 1.00
E(UnknownReadHandler): Invalid halfword read … pc 0x80042684
```

Classic **missing / wrong movie stream** during field movie play (MDEC decode of garbage).

## Root cause

v0.1.3 overwrote Cosmo maps with **pure CSR Disc 2** `WHITE2.DAT`, undoing the
intentional single-disc **movie trim** from earlier packs:

| Pack | WHITE2 PMVIE+MOVIE pairs |
|------|--------------------------:|
| CSR D1 / D2 | 2 (ids 28 + 42) |
| single-disc **0.1.2** | **0** (trimmed) |
| single-disc **0.1.3** | **2** (restored pure D2 — bad on D1) |

On Disc 1 those ids resolve to **GOLD2.MOV** / **JUNELEIN.STR**, not D2’s
FEELWIN1 / JUNAIRU. Wrong bitstream → MDEC/DMA crawl + glitches.

v0.1.3’s “hybrid WHITE2” finding was the **trim**, not corruption. LOSLAKE3
also lost one intentional pair removal in 0.1.3.

## Fix (v0.1.4)

Restore **0.1.2** `FIELD/WHITE2.DAT` and `FIELD/LOSLAKE3.DAT` on top of 0.1.3
(other Cosmo pure-D2 maps kept). Pairs on WHITE2 → 0 again.

## Lesson

Do not replace movie-trimmed single-disc DATs with pure multi-disc CSR scripts
unless the matching D2/D3 movies are on Disc 1 (or ids remapped).
