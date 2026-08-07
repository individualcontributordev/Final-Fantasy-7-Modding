# Status: post manip-movies todos under intentional-skip rule

## Rule

CSR/SD **skipped or removed Play** = intentional → **do not fix.**  
Manip **slot overwrites** = intentional.  
**Do fix:** seed payloads + hard seeks so movies that **still play** work; optional ending **stream** placement if you want credits video.

Full table: `docs/findings/2026-08-07-post-manip-movies-todo-triage.md`

## DROP (stop treating as bugs)

| Was on the “fix” pile | Why drop |
|--------------------------|----------|
| Unskip LAS4_0 / ENDING01 (pristine LAS4_0) | CSR+SD JMPF — intentional |
| Restore LAS4_2 / LAS4_3 Play | SD removed PMVIE — intentional |
| Full LASTMAP movie restore from pris/CSR | SD trim — intentional unless crash |
| Original D1 clips in JAIROFAL / GOLD7_2 / CAR_1209 / JAIROFLY | Manip seed hosts |
| LASTFLOR vs CANONON same slot | Known seed conflict — deferred by design |
| ending_v7 pristine LAS4_0 “so endings play” | Wrong under this rule |

## KEEP (real remaining work)

| Todo | Why |
|------|-----|
| **Manip seed verify** after every stack | CANONON→JAIROFAL, CANONON@250450 Form2, CANONHT2→CAR_1209, LAST4_3→GOLD7_2, LASTMAP.BIN→JAIROFLY |
| **LAST4_3 re-punch** if ending/other write hits GOLD7_2 | Seed integrity |
| **LASTMAP crash NOP** only if a live path still MOVIE’s Form1 id23 | Crash fix, not unskip |
| **Ending credits LBA/payload** (01/3E/2E) | Only if product wants credits **on disc**; no field JMPF skip of 26/29 — stream/seek problem |
| **Lake vs clean ENDING2E** at 250450 | Tradeoff, not a skip-restore |
| **Builder cleanup** | Don’t replace CSR/SD LAS4_0 with pris for ending tests |

## Healthy bar after manip-movies (no ending pack)

Playtest builder checks seed + LBA 250450.  
No field “restore skips” pass required.
