LIMIT THE FILE CONTENT TO AT MOST 150 LINES. IF MORE CONTENT NEEDS TO BE ADDED USE THE str-replace-editor TOOL TO EDIT THE FILE AFTER IT HAS BEEN CREATED.
# FIELD.BIN: PMVIE/MOVIE/MVIEF opcode handlers located (D2 Ghidra export)

**Date:** 2026-08-24
**Confidence:** confirmed (string cross-reference in disassembly)
**Status:** in-progress — handlers found, disc-read call site not yet found

## Summary

In the Disc 2 `FIELD.BIN.dec` Ghidra export, located the real field-opcode
dispatch table and the three movie-related opcode handlers by their debug
string literals. This supersedes the `PTR_PTR_800df11c` false lead from
earlier in this investigation.

## False lead first (teaching note)

Earlier in this session, `PTR_PTR_800df11c` (referenced from `FUN_800afefc`
at lines 7294/7301/7343/7360/7370/7451 of the C export) looked like a
promising opcode dispatch table — it's indexed by a byte pulled from
`param_1 + 1` and called as a function pointer. **It is not the opcode
table.** Reading the full function (`FUN_800afefc`, lines ~7280-7459) shows
its other cases call `setCopControlWord`/`getCopReg`/`copFunction` (PS1 GTE
coprocessor register access) and copy 32 bytes of data resembling a bone/
transform matrix. This is a model-rendering or animation dispatch, not the
field-script interpreter. Lesson: a function-pointer table indexed by a
byte is necessary but not sufficient evidence of "opcode dispatcher" — you
need a caller that reads the index byte directly from field-script data,
not from an already-decoded animation/render parameter struct.

## Discovery

**The real dispatcher:** `FUN_800baf54` (C export lines 13578-13624). Byte
`DAT_8009a058` is read directly from field script bytes (line 13611:
`DAT_8009a058 = *(byte *)(iVar2 + (uint)*puVar6);`, where `iVar2` derives
from `_DAT_8009c6dc`, the field script buffer pointer) and immediately used
to call a function pointer table: `(*(code *)(&PTR_LAB_800e0228)[DAT_8009a058])();`
(line 13613). This *is* indexed by raw opcode byte, matching field-script
semantics (loop terminates when the byte is 0, i.e. opcode 0x00 = script
end/no-op).

Table base: `PTR_LAB_800e0228` = `0x800e0228` (declared line 537 of the C
export). Each entry is a 4-byte function pointer, so opcode N is at
`0x800e0228 + N*4`.

Verified via the HTML listing (`workspace/ghidra/FIELD.BIN.dec_disc2.html`):

| Opcode | Table addr | Target | Debug string (proves handler identity) |
|--------|-----------|--------|------------------------------------------|
| 0xF8 (PMVIE) | `800e0608` | `LAB_800ccd54` | `s_pmvie_800a0be8` = `"pmvie"` |
| 0xF9 (MOVIE) | `800e060c` | `LAB_800cce94` | `s_movie_800a0bf0` = `"movie"` |
| 0xFA (MVIEF) | `800e0610` | `LAB_800ccfe8` | `s_mvief_800a0bf8` = `"mvief"` |

These three mnemonics (PMVIE = prepare movie id, MOVIE = play, MVIEF = wait
for movie finished) match the canonical FF7 field-opcode set used by Makou
Reactor and other prior RE. This is the first opcode-level confirmation in
this repo that these names correspond to real, distinct handler addresses
in `FIELD.BIN`, not just Makou's naming convention.

**Handler bodies (both `pmvie` and `movie` read/write the same struct):**
- Both operate on a struct at `DAT_8009c6e0` (a pointer, dereferenced then
  offset): byte at offset `+1` = an async-operation state (0/1/2/3), and a
  halfword at offset `+0x26` = a sub-state/counter.
- `LAB_800ccd54` (pmvie): if state byte `& 3 == 0`, logs `"pmvie"` via
  `FUN_800bead4` (a debug/trace call — same helper `movie`/`mvief` use for
  their own name strings), then branches on the state value to advance a
  per-field-object script-pointer/counter table at `0x80083200`-ish
  (`DAT_800722c4`-indexed halfword array). No CD/disc read call appears in
  this handler.
- `LAB_800cce94` (movie): similar shape — checks `DAT_800716cc`, sets a
  flag `DAT_80071c1c = 1`, and branches on a state value read from the
  `DAT_8009c6e0`-based struct (`+1` byte) against constants 0, 4, 5, 0x14 —
  looks like a state machine advancing an async request, not the actual
  media/CD-read routine itself.

## Why it matters

This confirms the field-script interpreter path for movie opcodes exists
in `FIELD.BIN` and gives exact addresses to keep tracing from, rather than
guessing at string-absent grep results (a full-text grep for "movie" in
the C-only export previously came back with **zero hits** — the strings
only exist as HTML-listing cross-references, since Ghidra's C decompile
output doesn't print referenced global string data inline the way the
listing does). This explains the earlier zero-hit grep result mentioned in
the previous exchange, and means: **when a decompile export shows no
matches for an expected string, check the HTML/ASCII listing before
concluding the string genuinely isn't present** — the C export can omit
string literal text even when the code clearly references it as a symbol
name (`s_pmvie_800a0be8`, etc.).

## Next steps

- Neither `pmvie` nor `movie` handler shown so far contains an obvious
  CD-read/seek call. The actual LBA seek (relevant to the CANONON hardcode
  investigation) is likely in a different state branch not yet read, or in
  a background/async task that these handlers merely request via the state
  flag (`DAT_80071c1c`, `DAT_8009c6e0+1`).
- Next: fully read `LAB_800cce94` (movie) past `800ccfa8`/`800ccfd8`, and
  read `LAB_800ccfe8` (mvief), tracing where `DAT_80071c1c` / the
  `DAT_8009c6e0` struct's state field get consumed elsewhere (search for
  writers/readers of `DAT_80071c1c` and `_DAT_8009c6dc`/`_DAT_8009c6e0`
  outside these three handlers) to find the actual disc-read/CD-seek call.

## Sources

- `workspace/ghidra/FIELD.BIN.dec_disc2.c` (lines 13578-13624: `FUN_800baf54`
  dispatcher; lines 7280-7459: `FUN_800afefc`, the false-lead GTE dispatch)
- `workspace/ghidra/FIELD.BIN.dec_disc2.html` (lines 51100-51330: `pmvie`/
  `movie`/`mvief` handler disassembly and string xrefs; lines 95157-95159:
  `PTR_LAB_800e0228` table entries at `800e0604`-`800e060c`)
