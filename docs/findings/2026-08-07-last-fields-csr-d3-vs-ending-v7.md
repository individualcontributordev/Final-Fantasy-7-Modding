# Last fields: CSR D3 vs ending-v7 D1

**Date:** 2026-08-07

Compared decoded `FIELD/*.DAT` (and movie opcodes) across:
CSR D3 · pristine D3/D1 · single-disc core · ending_v7 bin.

## Identical (CSR D3 == ending_v7)

`LAS4_1`, `LAS0_1`…`LAS0_8` — full decode match.

## Differ (movie-relevant)

| Field | CSR D3 | ending_v7 | Notes |
|-------|--------|-----------|-------|
| LASTMAP | PMVIE 23+24; AD S31=`MVCAM+MOVIE`; AD3 has late MOVIE | PMVIE 23+24; AD S31=`MVCAM`+NOP; AD3 late MOVIE kept | v5 NOP of early id**23** (LASTMAP.BIN Form1 crash). CSR D3 still plays it. |
| LAS4_0 | PMVIE **25** + MOVIE; +2 CSR JMPFs | PMVIE **25** + MOVIE; **pristine** (no CSR JMPFs) | Ending work restored D1 pris; movie not skipped. |
| LAS4_2 | PMVIE **20** (LAST4_2) + MOVIE | **no** PMVIE/MOVIE | SD-core skip, still on ending_v7 |
| LAS4_3 | PMVIE **21** (LAST4_3) + MOVIE | **no** PMVIE/MOVIE | SD-core skip, still on ending_v7 |
| LAS4_4 | PMVIE **21** + CSR JMPF/MAPJUMPs | PMVIE **21**; SD-core jump layout | Movie present; routing differs from CSR D3 |

## Movie IDs (D3 MOVIE_ID)

| id | File |
|---:|------|
| 20 | LAST4_2.BIN |
| 21 | LAST4_3.BIN / used in LAS4_3+LAS4_4 |
| 23 | LASTMAP.BIN |
| 24 | LASTFLOR.MOV |
| 25 | ENDING01.MOV |
| 26 | ENDING3E.MOV |
| 29 | ENDING2E.MOV |

## vs user hypothesis

Hypothesis: “CSR skips some movies; D1 ending work restored default.”

| Claim | Reality |
|-------|---------|
| CSR D3 skips end movies | **No** — CSR D3 keeps ids 20/21/23/24/25 |
| ending_v7 restored all defaults | **Partial** — LAS4_0 → pris (good for ENDING01); LASTMAP early MOVIE still NOP’d; **LAS4_2/3 still skipped** (SD core, not CSR) |

SD core was more aggressive (stripped LASTMAP PMVIE/MOVIE entirely). Ending v5/v7 put PMVIE 23/24 back but kept early MOVIE NOP’d.

## Recommendation

If goal is CSR D3 endgame script parity:

1. Keep LASTMAP AD S31 MOVIE NOP (needed on single-disc — id23 is Form1).
2. Optionally re-apply CSR LAS4_0 JMPFs (speedrun/routing only; movie already plays).
3. Restore LAS4_2 / LAS4_3 movie ops from CSR D3 / pris (ids 20/21) if those short crater FMVs are desired — seeds already protect LAST4_3 body in GOLD7_2.
