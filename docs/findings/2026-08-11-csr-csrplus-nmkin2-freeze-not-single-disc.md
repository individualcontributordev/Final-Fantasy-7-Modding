# Finding: Early freeze field 122 (NMKIN_2) on CSR + CSR+ (no Single-disc)

**Date:** 2026-08-11  
**Report:** CSR + CSR+ only (no Single-disc). Freeze at start of game on **field 122** after the elevator when walking down the stairs.

## Map IDs

| ID | Map |
|----|-----|
| 121 | ELEVTR1 |
| **122** | **NMKIN_2** (No.1 reactor, post-elevator walkway/stairs) |
| 120 | NMKIN_1 |
| 125 | NMKIN_5 (Guard Scorpion area) |

## What is not the cause

### Single-disc
Ruled out by the human build (CSR + CSR+ only).

### CSR+ scene packs (disc1 layers)
Applied against plain CSR D1 image and checked:

| Check | Result |
|-------|--------|
| Files whose sector ranges change | Only pack targets: BLIN66_6, BLIN70_4, CANON_2, EALS_1, FSHIP_24, LAS*, LOSLAKE1 |
| **FIELD/NMKIN_2.DAT / .MIM / .BSX** | **Identical** to CSR-only |
| FIELD/ELEVTR1.* | Identical |
| Spill into neighbors | None |
| Directory size updates | Only the 10 claimed pack files (within same sector alloc) |

CSR+ disc1 layers were mostly built vs CSR+Single-disc image size (originalBytes 748775664), but on plain CSR their absolute offsets still land on the correct late-game FIELD/*.DAT extents + FIELD dir size bytes. They do **not** rewrite NMKIN_2.

So **CSR+ is very unlikely to be the direct field-122 corruption source.**

## What does change on this path

| Asset | pristine vs CSR base | CSR vs CSR+CSR+ |
|-------|----------------------|-----------------|
| NMKIN_2.DAT/MIM/BSX | **SAME** | SAME |
| ELEVTR1.* | SAME | SAME |
| **NMKIN_1.DAT** | **DIFF** (CSR trim on evb/3) | SAME |
| MD1STIN, MD1_1, NMKIN_5 | DIFF (CSR trims) | n/a for stairs |

CSR changelog historically trims up to Guard Scorpion / reactor 1 / elevator-adjacent scenes. Field 122 itself is stock; softlock may still be **flag / party / UC state** left by an earlier CSR-trimmed map (e.g. NMKIN_1 evb/3 dialogue/PRTYE path).

### NMKIN_1 CSR delta (summary)
evb/3: CSR shortens the post-event chain (fewer REQEW + drops WINDOW/MESSAGE before RET on the early path). Dead bytes after RET retain old ops. Worth a CSR-only playtest on the NMKIN_1 to elevator to NMKIN_2 stairs route.

## Prior related reports
- Elevator softlock with Single-disc+CSR+ was blamed on **layer apply order** (CSR+ before Single-disc). Builder now applies Single-disc first. This new report is **without** Single-disc.
- Post-Guard Scorpion freeze (SOUTHMK / BATRES / CLOUD.BCX CD log) is a **later** point on the same reactor exit path; may or may not share root cause.

## Next isolation (human)
1. **CSR only** (no CSR+, no Single-disc, no Fanfare) then cold boot then elevator then field 122 stairs.
2. If CSR-only OK: add CSR+ all-or-none, same route.
3. Paste APPLIED.txt + freeze yes/no for each.

## Status
Root cause **not fixed**. CSR+ binary integrity on NMKIN_2 verified clean; isolate **CSR base** vs **CSR+** with the retest above.
