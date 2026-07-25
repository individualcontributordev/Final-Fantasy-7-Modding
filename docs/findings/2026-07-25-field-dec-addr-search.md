# FIELD.BIN.dec encounter address byte search

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Source:** `docs/windows-last-output.txt` (search on 264008-byte `.dec`)

## Results

| Needle | Hits |
|--------|------|
| Full u32 ptrs (StepID/Offset/Danger/Formation/RNG VA) | **0** |
| RNG table head `B1CAEE6C…` | **1** @ file `0x40638` / va `0x80040638` |
| u16 `40 C5` (0xC540) | **3** @ `0xB9CC`, `0xB9DC`, `0xB9E4` |
| u16 `09 80` (lui imm noise) | many |

## Interpretation

- Table is in this binary; absolute `0x8009C540`-style pointer words are not embedded.
- StepID is likely `lui 0x8009` + `lbu/sb …, 0xC540(reg)` — inspect the three `0xC540` sites in Ghidra first.
