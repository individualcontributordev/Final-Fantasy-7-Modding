# SD core: intentional Play skips vs ending movies to fix

**Date:** 2026-08-07  
**Policy:** If Play Movie is skipped after SD core, **report** — do not auto-unskip.  
**Except:** ending streams broken for non-skip reasons (missing LBA / wrong Form / stomped file) still fix.

## After pristine D1 → CSR D1 → SD core only

### JMPF still present (ops left, jumped over)

| Field | Skip | Source |
|-------|------|--------|
| **LAS4_0** | JMPF over **PMVIE 25 + MOVIE** = **ENDING01** | Same as **CSR D3** LAS4_0 (core copies it) |

User recollection: ending movies were **not** meant to be field-skipped for single-disc.  
That JMPF is **CSR’s** endgame skip, pulled in with SD core’s D3 field set — not a separate “broken ending” edit. Treat as **intentional CSR/SD behavior** unless product goal is “play ENDING01 on SD.”

### Ops removed by SD core (not JMPF)

| Field | Removed | Notes |
|-------|---------|-------|
| **LASTMAP** | PMVIE **23**, **24** (LASTFLOR); all MOVIE | SD trim, **≠** CSR D3 (CSR still has ops + early JMPF) |
| **LAS4_2** | PMVIE **20** LAST4_2 | Short crater FMV — typical intentional trim |
| **LAS4_3** | PMVIE **21** LAST4_3 | Same |

**LASTFLOR (24)** is end-adjacent; stripped only on SD LASTMAP, not via CSR JMPF.

### Ending IDs 26 / 29 after SD core

No LAS4_*/LASTMAP JMPF skip of ENDING3E (26) or ENDING2E (29).  
Play path issues for long credits are **disc payload / absolute LBA**, not field JMPF (see ending v6–v7 work).

## ending_v7 field mistakes vs this policy

| Change | Was it right under this policy? |
|--------|----------------------------------|
| Full **pristine LAS4_0** to unskip ENDING01 | **Only if** goal is play ENDING01; should have **asked** (CSR/SD skip is intentional upstream) |
| LASTMAP v5 AD S31 MOVIE NOP | OK as **crash** fix (id23 Form1), not “restore skip” |
| Ending LBA alias + CANONON punch | Correct class of fix for broken **ending streams** |

## Going forward

1. After SD core: list JMPF-over-Play and deleted PMVIE/MOVIE; flag intentional candidates.  
2. Do **not** replace CSR/SD fields with pristine to “fix” skips without confirmation.  
3. **Do** fix ending if streams missing/wrong at seek LBAs or MOVIE_ID/engine hard seeks fail.
