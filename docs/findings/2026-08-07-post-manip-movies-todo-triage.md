# Post manip-movies todo triage (intentional-skip rule)

**Date:** 2026-08-07  
**Stack:** D1 pris → CSR D1 → SD core → manip-movies 0.1.2 (+ optional ending test)  
**Rule:** CSR/SD **field skips** (JMPF or removed Play) = intentional → **do not “fix.”**  
Manip seed overwrites of D1 movie slots = intentional.  
**Do fix:** payload/LBA/crash so a movie that **scripts still play** actually works.

## DROP — intentional (no fix)

| Item | Why drop |
|------|----------|
| Unskip **LAS4_0 ENDING01** (pris LAS4_0 / kill JMPF) | CSR D3 + SD core JMPF skip — speedrun |
| Restore **LAS4_2 / LAS4_3** Play (ids 20/21) | SD core removed PMVIE — trim |
| Full pristine/CSR LASTMAP “restore all movies” | SD stripped 23/24+MOVIE; only patch if crash |
| Mid-game D1 clips lost to manip **slot** hosts (CAR_1209, GOLD7_2, JAIROFAL, JAIROFLY originals) | Seed overwrite — manip needs those bodies |
| LASTFLOR into JAIROFAL | Seed note: conflicts with CANONON for LOSLAKE1 |
| Whitelist “never ENDING2E full on CD without tradeoff” as field unskip | Size/LBA, not a skipped Play op |
| ending_v7 “fix skip” of ENDING01 via pristine LAS4_0 | Was wrong under this rule — **revert intent** |

## KEEP — real breakage / product (if goal is play path)

| Item | Why still a todo | Notes |
|------|------------------|-------|
| **LOSLAKE1 / CANONON @ LBA 250450** Form2 | Script **plays**; hard seek | Seed + alias — **keep** |
| **CANONON body in JAIROFAL** | Same manip path | Seed — **keep** |
| **CANONHT2 in CAR_1209** | CANON_2 still plays on CSR | Seed — **keep** |
| **LAST4_3 body in GOLD7_2** | Seed; stomped if ending alias | Restore after any ENDING2E write — **keep** |
| **LASTMAP.BIN in JAIROFLY** | Seed payload for maps that still PMVIE 23 | Field may skip play on SD LASTMAP; payload still for other maps/manips — **keep seed** |
| **LASTMAP crash** if something still **MOVIE** id23 Form1 | Engine crash, not skip | Minimal NOP only if path still hits MOVIE |
| **Ending credits streams** (01/3E/2E) at **absolute D3 LBAs** | No field JMPF skip of 26/29; engine hard-seeks | Only if product wants credits **play**; else optional |
| CANONON hole **inside** ENDING2E @ 250450 | Mutual exclusion on CD | Design choice: lake vs clean credits — not a “skip fix” |
| Clean builder: **stop** pristine LAS4_0 for endings | Align with rule | Use LBA/payload only; leave SD/CSR LAS4_0 |

## NOT a post-manip field-restore list

- Collateral D1 movies under ending LBA ranges (ONTRAIN, FALLPL, …) — discarded for space/alias, not CSR Play restores.
- Blackbg / junbin JMPFs that skip shared movie ids — CSR/SD as shipped; out of scope unless manip-specific.

## Minimal “healthy after manip-movies” checklist

1. Seed four bodies + CANONON@250450 verify (playtest builder already).  
2. Do **not** re-apply pristine end fields.  
3. Optional product track: ending LBA alias **without** unskipping LAS4_0; accept mid-ENDING2E hole or drop lake.  
4. LAST4_3 restore **only** if ending (or other) write stomps GOLD7_2.

## Seed reference

`mods/single-disc/patches/csr-manip-movie-seed.txt` — LAST4_3, LASTMAP.BIN, CANONHT2, CANONON→JAIROFAL.
