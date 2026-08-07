# Status: CSR base (D1) vs CSR D3 ending skips

## Name note

Playtest/ending builders do **not** write `ff7_d1_csr_base_local.bin`.  
Step 1 of the stack is pristine D1 + CSR **disc1** layer = same as:

`workspace/iso-extract/ff7_d1_csr_base.bin`

## Answer

**CSR base (D1) does not have the ending movie skips you see in Makou on CSR D3.**

| | LAS4_0 skip ENDING01 | LASTMAP early JMPF |
|--|----------------------|--------------------|
| Makou CSR **D3** | Yes | Yes |
| `ff7_d1_csr_base.bin` (CSR D1 only) | **No** (still pristine fields) | **No** |
| After **single-disc core** on D1 | **Yes** (file == CSR D3 LAS4_0) | **No** (SD LASTMAP trim, different from CSR) |
| ending_v7 | **No** (pris LAS4_0 put back) | **No** (+ our AD S31 MOVIE NOP) |

CSR **disc1** layer never patches LASTMAP/LAS4_*. Those JMPF skips live on **CSR disc3**.  
Single-disc core is what first pulls CSR-like LAS4_0 (with ENDING01 skip) onto the D1 image; ending build then overwrites LAS4_0 with pristine so ENDING01 can play.

Detail: `docs/findings/2026-08-07-csr-base-vs-d3-ending-skips.md`
