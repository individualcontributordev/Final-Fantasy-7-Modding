# CSR D3 ending movie skips (JMPF) vs ending-v7

**Date:** 2026-08-07  
**Source:** CSR D3 image vs pristine D3 vs `ff7_d1_playtest_ending_test.bin`  
**User check:** Makou on CSR-layered D3 — confirmed skips.

## How CSR skips (not by deleting PMVIE)

Ops stay in the script; **unconditional JMPF** jumps over Play Movie.

### LAS4_0 — skip ENDING01 (id 25)

| Build | dic S0 before final battle |
|-------|----------------------------|
| D3 pristine | `FADE` → **PMVIE 25** → **MOVIE** → battle |
| **CSR D3** | `FADE` → **JMPF +4** → *(skips PMVIE+MOVIE)* → battle |
| **ending_v7** | same as **pristine** (plays ENDING01) |

CSR keeps the PMVIE/MOVIE bytes; JMPF never lands on them. Makou shows “skip ending1”.

### LASTMAP — skip early Play path (id 23 setup)

| Build | AD3 S31 start | AD S31 |
|-------|---------------|--------|
| D3 pristine | `UC` `MENU2` **REQEW…** (runs) | `MVCAM`+**MOVIE** |
| **CSR D3** | `UC` `MENU2` **JMPF +0x36** → skips first block including **REQEW→AD S3** (PMVIE 23) + REQSW AD S5 | `MVCAM`+**MOVIE** still present |
| **ending_v7** | pristine path (no CSR JMPF) | `MVCAM`+**NOP** (v5 Form1 fix) |

So CSR’s LASTMAP skip is the **early JMPF** over the REQ that queues PMVIE 23.  
ending_v7 does **not** have that CSR jump; it only NOPs AD S31 MOVIE (different edit).

AD3 S31 late **MOVIE** (after party talk, toward LASTFLOR path) remains on pris, CSR, and ending_v7.

## ending_v7 vs CSR D3 (your question)

| Field | CSR D3 intent | In ending_v7? |
|-------|---------------|---------------|
| LAS4_0 skip ENDING01 | JMPF over id 25 | **No** — restored pristine (movie plays) |
| LASTMAP skip early play | JMPF over REQ→AD S3 | **No** — pristine AD3 start |
| LASTMAP AD S31 MOVIE | still there on CSR | **NOP’d** on v7 (our crash fix, not CSR) |

## Why earlier scan missed this

Counting PMVIE/MOVIE opcodes only → CSR still “has” ids 23/24/25.  
Need **JMPF reachability** (or Makou disable flags) to see skips.

## Implication for single-disc

ending_v7 deliberately left CSR end skips off when we put pris LAS4_0 / patched LASTMAP for movie recovery.  
To match **CSR D3 speedrun skips** again: re-apply CSR LAS4_0 + CSR LASTMAP (or only the two JMPFs), while keeping AD S31 MOVIE NOP if id23 stream is still Form1 on D1.
