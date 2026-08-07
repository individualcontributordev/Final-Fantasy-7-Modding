# Status: CSR D3 ending movie skips vs ending-v7

## What CSR D3 actually does

Skips are **JMPF over Play Movie**, not deleted ops. Makou shows them; opcode-count misses them.

| Field | CSR D3 skip | ending_v7 |
|-------|-------------|-----------|
| **LAS4_0** | `JMPF` jumps over **PMVIE 25 + MOVIE** (ENDING01) before final battle | **No skip** — pristine path, ENDING01 **plays** |
| **LASTMAP** | Start of AD3 S31: `JMPF +0x36` skips early block including **REQ→AD S3** (PMVIE 23 setup) | **No CSR jump** — pristine start; separate v5 **NOP** on AD S31 MOVIE only |

So: CSR left those end movies “present but unreached.” ending_v7 does **not** carry those CSR jumps (LAS4_0 was replaced with pristine for ending work).

## Not the same edit

- CSR LASTMAP: skip via early JMPF (AD S31 MOVIE still in file).  
- ending_v7 LASTMAP: AD S31 MOVIE NOP’d (Form1 crash); no CSR JMPF.

Detail: `docs/findings/2026-08-07-csr-d3-ending-movie-jumps.md`

## If you want CSR skips on the single-disc ending bin

Re-apply CSR D3 `LAS4_0.DAT` + CSR D3 `LASTMAP.DAT` (or only the two JMPFs), and keep the AD S31 MOVIE NOP if id23 is still not a real stream on D1.
