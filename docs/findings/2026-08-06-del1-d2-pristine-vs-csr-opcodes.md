# DEL1 (field 441) — pristine D2 vs CSR D2

Decoder: Makou `Section1File` + `Opcode::length`/`names` (local makoureactor);
LZS via CSR `scripts/lzs.py` (ff7tk-compatible); dialog via ff7tk `FF7Text` eng.

## Summary

| | pristine D2 | CSR D2 | delta |
|--|--:|--:|--:|
| compressed `.DAT` | 21700 | 21456 | −244 |
| LZS decompressed | 42956 | 42512 | −444 |
| script section 0 | 12876 | 12432 | −444 |
| sections 1–6 | identical | identical | 0 |
| script opcodes (20 entities, 106 slots) | **identical** | **identical** | 0 |
| AKAO block | identical | identical | 0 |
| dialog **content** (to `0xFF`) | 5661 B stream | same stream | 0 |
| dialog **padding** after `0xFF` | 446 B | 2 B | **−444** |

## Conclusion

**CSR did not change any field script on DEL1 for Disc 2.**

Binary size diffs (−244 compressed / −444 decompressed) are only a
**Makou-style re-save of the text block**: gap bytes between one string’s
`0xFF` and the next string start were stripped. All 69 dialog payloads
(through `0xFF`) are byte-identical. Entity names, script pointer table,
and every decoded opcode match.

Manual script inspection finding “nothing” was correct.

### Padding-only text ids (content same)

| text id | pris span | csr span | pad removed |
|--------:|----------:|---------:|------------:|
| 35 | 80 | 40 | 40 |
| 37 | 220 | 62 | 158 |
| 56 | 117 | 31 | 86 |
| 62 | 213 | 110 | 103 |
| 65 | 168 | 111 | 57 |

Pristine gaps hold leftover authoring junk (ASCII fragments in hex). CSR
offsets for ids ≥36 shift earlier by cumulative pad removal; last ids −444.

### Method

1. Extract `FIELD/DEL1.DAT` from pristine D2 and CSR D2 layer-on-pristine.
2. LZS decompress (`u32le` size + Okumura payload).
3. PS header: 7 VRAM ptrs → file offs via `vramDiff = ptr0 − 28`.
4. Section 0 = scripts + texts + AKAO; opcode-decode every entity/slot;
   compare text payloads truncated at `0xFF`.

Reproduce (scratch): `python3 workspace/tmp_del1_ops.py`,
`python3 workspace/tmp_del1_texts.py`.
