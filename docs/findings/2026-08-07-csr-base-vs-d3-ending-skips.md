# CSR base (D1) vs CSR D3 ending movie skips

**Date:** 2026-08-07

User checked Makou on CSR-layered **Disc 3** (ENDING01 skip in LAS4_0, early play skip in LASTMAP).  
Compared that to the D1 build intermediate often called CSR base (`ff7_d1_csr_base.bin` = pristine D1 + CSR **disc1** layer only).

Build path (playtest / ending v7):

1. pristine D1  
2. CSR **disc1** layer → CSR base (`ff7_d1_csr_base.bin` matches this)  
3. single-disc core  
4. manip-movies 0.1.2  
5. (ending only) LASTMAP v5 + **pristine** LAS4_0 + ending LBAs…

Scripts do not write `ff7_d1_csr_base_local.bin` by that name; step “CSR base” is the same image as `workspace/iso-extract/ff7_d1_csr_base.bin`.

## Do ending skips exist on each image?

| Image | LAS4_0 JMPF over ENDING01 (id 25) | LASTMAP AD3 early JMPF (CSR) | Notes |
|-------|-----------------------------------|------------------------------|-------|
| D1 / D3 pristine | No | No | Vanilla plays movies |
| **CSR disc1 layer / csr_base.bin** | **No** | **No** | Fields still **D1 pris** — CSR D1 layer has **no** LASTMAP/LAS4_* records |
| **CSR Disc 3** | **Yes** | **Yes** | Real CSR endgame skips (Makou) |
| + single-disc core on D1 | **Yes** (== CSR D3 LAS4_0) | **No** | Core copies CSR D3 LAS4_0; LASTMAP is SD trim (AD S31 MOVIE gone), not CSR early JMPF |
| playtest movies | Yes (from core) | No | |
| ending_v7 | **No** (pris LAS4_0 restored) | No | + v5 AD S31 MOVIE NOP |

## Takeaway

- **CSR D3:** skips end movies (JMPF), leaves ops in file.  
- **CSR base on D1:** does **not** include those Disc 3 field edits. End maps stay vanilla until **single-disc core** (LAS4_0) or ending patches.  
- To match Makou-on-CSR-D3 skips on a single-disc D1 bin: need CSR D3 (or SD-core) LAS4_0 **and** CSR D3 LASTMAP early JMPF — ending_v7 currently removes the LAS4_0 skip on purpose.

## Verify

```bash
# csr_base == D1 + CSR disc1 only (no end skips)
python3 -c "..."  # see finding session / compare Field LAS4_0 to CSR D3
```
