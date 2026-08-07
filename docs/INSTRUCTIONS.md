# Status: after SD core — report Play skips; fix ending streams only

## Rule (from you)

If a **Play Movie is skipped** after single-disc core → **tell you** (likely intentional).  
Do **not** auto-unskip with pristine field replaces.  
**Do** fix ending movies when **broken** (missing data / bad LBA / crash) — you did **not** skip those with JMPF for single-disc.

## After D1 + CSR D1 + SD core (before ending hacks)

| What | Status | Action |
|------|--------|--------|
| **LAS4_0 JMPF → skip ENDING01 (25)** | Present (= CSR D3 file) | **Report only** — CSR/SD intentional unless you want it played |
| **LAS4_2 / LAS4_3** PMVIE removed | SD trim (ids 20/21) | Report — intentional crater cuts |
| **LASTMAP** PMVIE 23/24 + MOVIE stripped | SD (not CSR D3) | Report — not “restore full pris” by default |
| **ENDING3E / ENDING2E** field JMPF | **None** on LAS4/LASTMAP | Broken credits = **payload/LBA** fixes, not field unskip |

## ending_v7 field step

Replaced **LAS4_0 with pristine D1** only to force ENDING01 to play for credits testing. That **undid** the CSR/SD skip without asking. Better: leave CSR/SD LAS4_0 and fix stream placement only; unskip ENDING01 only if you decide skips are wrong for this mod.

## Detail

`docs/findings/2026-08-07-sd-core-play-skips-vs-ending.md`
