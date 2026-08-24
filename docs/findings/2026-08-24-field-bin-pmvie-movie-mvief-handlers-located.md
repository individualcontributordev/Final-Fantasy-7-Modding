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

## Update 2026-08-24 (same day, continued): all three handlers fully read — still no CD call

Read the complete `LAB_800cce94` (MOVIE, `800cce94`-`800ccfe4`) and
`LAB_800ccfe8` (MVIEF, `800ccfe8`-`800cd0c0`) bodies in the HTML listing.
Findings:

- **MOVIE handler struct layout confirmed:** `DAT_8009c6e0+1` = state byte
  (values seen: 0/1/3/4/5/0x14), `+0x26` = halfword sub-state (0/1/2), and
  **`+2` (halfword) = the movie ID itself** — written at `800cce7c`
  (`sh v0,0x2(v1)` where `v0` came from the PMVIE-set byte at `+1`, i.e.
  PMVIE's opcode-operand byte is relayed into struct offset `+2`). This
  is the first concrete evidence of *where* the raw movie-id byte from the
  field script ends up living for later use.
- **Searched every reference to `_DAT_8009c6e0` in the C export
  (`grep -n "_DAT_8009c6e0" ... | 60+ hits`) for any read of offset `+2`
  elsewhere in the file — there are none.** Offset `+2` is written once
  (PMVIE handler) and zero-initialized once (struct-init function, line
  13337); no other function reads it. Either (a) the movie ID is consumed
  through a different aliasing path the decompiler didn't resolve back to
  `_DAT_8009c6e0` (e.g. a raw pointer passed around and dereferenced with a
  local variable name only, not the global symbol), or (b) it's read by
  something outside `FIELD.BIN` entirely (kernel exe or a different
  overlay) via a shared low-memory struct.
- **MVIEF handler (`LAB_800ccfe8`) calls `FUN_800c0248`** with
  `a2 = *(short)(DAT_8009c6e0 + 0x88)` — **not** offset `+2` (the movie ID
  slot). Read `FUN_800c0248` fully: it's a **generic field-script operand
  decoder** with 21 call sites across unrelated opcodes (movement,
  dialogue, etc. — call sites at `800ca448`, `800ca54c`, `800cb8b0`, etc.),
  switching on `a0` (1-6) to fetch a byte/word from the script buffer
  `_DAT_8009c6dc` at various computed offsets. It is **not movie-specific**
  and contains no CD/media call — ruled out as a dead end for this trace.
- **Struct offset `+0x88`** (read by MVIEF before calling the generic
  decoder) is a different field entirely from the movie-id slot at `+2`;
  not yet identified what it represents.

### Conclusion so far

The field-script opcode handlers (PMVIE/MOVIE/MVIEF) only stage state in
the `DAT_8009c6e0` struct and never call any CD/disc-read primitive
directly. The actual movie playback trigger must be in a **different,
not-yet-located function** — most likely a per-frame background task
(polled outside the opcode interpreter loop) that reads the state flag
`DAT_80071c1c` and/or struct offset `+1`/`+0x26`, resolves the movie id
at struct `+2` to an LBA (via `MOVIE_ID.BIN` normally, but hardcoded for
CANONON per the confirmed live test), and issues the actual seek. This
function has not yet been located; searching for `DAT_80071c1c` reads
(not writes) across the whole export, or for functions that reference
`DAT_8009c6e0 + 2` via a copied/aliased pointer rather than the global
symbol directly, are the two open threads.

### Updated next steps

- The `_DAT_8009c6e0`-prefixed grep only catches direct global-symbol
  references. Search instead for the raw hex offset pattern in the struct
  init function (`FUN_...` around line 13258-13385, where `_DAT_8009c6e0 =
  param_1;`) to find what else holds a copy of `param_1` — that caller may
  pass the same struct pointer into a totally different function under a
  different local name, hiding the `+2` read from a symbol grep.
  Concretely: find the caller of the struct-init function (the one setting
  `_DAT_8009c6e0 = param_1` at line 13258) and read forward from there for
  a per-frame "movie service" routine.

### Update 2026-08-24 (continued further): traced the init/update call chain — also a dead end

Found and read the callers:
- `FUN_800ba534` (line 13247, sets `_DAT_8009c6e0 = param_1` at 13258) is
  called once, from the main field-object loop at line 954:
  `FUN_800ba534(&DAT_8009abf4, 0x80074ea4, *_DAT_8007eb64);` — this is
  one-time field-object **initialization**, not a per-frame movie poller.
- The per-frame **update** counterpart is `FUN_800ba65c` (line 13283),
  called once per frame from the same outer loop. It calls, in order:
  `FUN_800d4bfc`, `FUN_800bc338`, `FUN_800d7d6c`, `FUN_800d7f9c`,
  `FUN_800bb3a8`, then **`FUN_800bc438(param_1)`** (line 13310) — the same
  `FUN_800bc438` already read earlier in this doc's first pass.
- Re-confirmed `FUN_800bc438` → `FUN_800bc4d4`: this pair only manipulates
  screen-space sprite/UI-icon coordinates clamped to `0x140`x`0xe0`
  (320x224, the PSX field-view resolution) and a double-buffered icon-slot
  index (`DAT_80114490`). **This is a UI icon/marker overlay routine, not
  movie playback** — another near-miss on the same struct offsets
  (`DAT_8009c6e0+0x32`, matching offsets touched by PMVIE), not a
  dead-end-worthy rabbit hole to repeat, but confirmed not to contain any
  CD call either.
- **None of the 5 sibling calls in `FUN_800ba65c`** (`FUN_800d4bfc`,
  `FUN_800bc338`, `FUN_800d7d6c`, `FUN_800d7f9c`, `FUN_800bb3a8`) have been
  read yet — any one of these five is a more promising unexplored lead
  than re-deriving `FUN_800bc438`, since they're unread and sit in the
  same per-frame update call chain.

### Next steps (revised, most promising first)

1. Read `FUN_800bb3a8`, `FUN_800d7d6c`, `FUN_800d7f9c`, `FUN_800d4bfc`,
   `FUN_800bc338` in that order (unread siblings of `FUN_800bc438` inside
   the confirmed per-frame update function `FUN_800ba65c`) — one of these
   is the more likely candidate for a movie-state poller, since they run
   every frame alongside (not instead of) the UI-icon routine already
   ruled out.
2. Alternatively, grep the whole export for reads (not writes) of
   `DAT_80071c1c` outside `FUN_800baf54`/`FUN_800bc4d4` — only one read
   site is known so far (`FUN_800bc4d4`, already ruled out as UI/icon
   code), so a second consumer likely exists elsewhere and hasn't been
   found by symbol grep yet, possibly because it's aliased through a
   pointer rather than referenced by the `DAT_80071c1c` symbol directly.

## Update 2026-08-24 (continued further still): sibling functions read, struct+2 confirmed generic — pivoting to dynamic tracing

Read all five sibling calls in `FUN_800ba65c` in full:

- **`FUN_800bb3a8`** (13683-13833): message-window/entity-icon tick + the
  field-script opcode interpreter's per-frame execution driver — this is
  the loop that calls `(*(code *)(&PTR_LAB_800e0228)[DAT_8009a058])()`,
  i.e. it **is** the frame-by-frame opcode dispatcher caller (not a
  separate poller). It contains no CD-read call of its own; it just runs
  script opcodes (including PMVIE/MOVIE/MVIEF) until the frame's op budget
  is exhausted. Its callee `FUN_800bbbcc` (message-window color/animation
  ticker) — also read fully — is unrelated (character head-plate flicker
  and message-box border colors, keyed off `DAT_8007eb98`/opcode-actor
  ids, not movies).
- **`FUN_800d7d6c`** (18255-18341) and **`FUN_800d7f9c`** (18347-18381):
  both are one-time **menu/UI panel setup** for a debug/status overlay —
  `FUN_800d7d6c` initializes fixed VRAM tile records (icon glyph slots,
  clock digits) and calls `func_0x80044a68` (a sprite/TIM draw primitive)
  6 times; `FUN_800d7f9c` builds text-label sub-windows ("Author", "Event",
  "Stop", "Step", "Actor OFF", "Info OFF") via `FUN_800d828c`/`FUN_800d9f00`
  and sets `DAT_80071c08 = 5` (a menu-page id, unrelated to
  `DAT_80071c1c`, the near-identical name is coincidental). No CD/media
  calls in either.
- **`FUN_800d4bfc`** (16940-16961): trivial 4-entry array zero-init
  (`DAT_80071e2c = 0`); no CD logic.
- **`FUN_800bc338`** (14030-14063, already partially quoted above): HUD
  clock-digit position/style init (`DAT_800e48f7` etc, screen coords);
  no CD logic.

**None of the five siblings contain a CD call.** This closes out the
`FUN_800ba65c` call chain as a dead end for this trace — every function
reachable from the confirmed per-frame object-update entry point has now
been read.

### struct offset +2 / +0x26 confirmed to be a generic per-opcode async-id slot, not movie-specific

Re-scanned the *entire* HTML listing (not just the C export) for every
instruction that loads `DAT_8009c6e0` into a register and then does
`sh reg,0x2(reg)` shortly after (i.e. every write to struct offset `+2`,
using raw address proximity instead of relying on the decompiler
resolving the global symbol). Found **two more writers** beyond the PMVIE
handler already documented:

- `800c45ac`-`800c4694` — the **`batle`** opcode handler (string xref
  `s_batle_800a0864`) — writes struct `+2` at `800c4638` with the return
  value of `FUN_800bf908` (a distinct battle-id-lookup helper, not the
  movie-id byte).
- `800c4ee8`-onward — the **`tutor`** opcode handler (string xref
  `s_tutor_800a08c0`) — writes struct `+2` at `800c4f5c` with a value
  computed from `DAT_800722c4` (current script-object index) through a
  lookup table at `0x800831fc`, again unrelated to movies.

**Conclusion:** offset `+2` (and its paired sub-state halfword at
`+0x26`) is a **generic "pending async operation id" slot shared by
multiple unrelated field-script opcodes** (`pmvie`, `batle`, `tutor`,
and likely others) — each opcode handler stashes its own kind of pending
id there and a *shared* completion-poll mechanism (state byte at `+1`)
advances it. This means grepping for reads of struct `+2` specifically
was always going to be a dead end for isolating the *movie* consumer,
since any reader must also branch on which opcode's async operation is
in flight — that branch/dispatch has not been located.

### Reassessment: static grep tracing has reached diminishing returns

After three extended sessions of pure static-decompile tracing (this
document + the two "Update" sections above), every function directly and
transitively reachable from the three opcode handlers and the per-frame
object-update entry point has been read, with **no CD/disc-read primitive
found anywhere in `FIELD.BIN`'s decompiled/disassembled text**. Two
explanations remain, both requiring a different technique than more
grepping:

1. The CD-read call is issued through a **function-pointer table call**
   the decompiler could not resolve to a fixed target (several `(*(code
   *))()` indirect calls exist in this file beyond the confirmed opcode
   table — e.g. inside `FUN_800bbbcc`'s per-actor state switch), so a
   plain-text search for `CdControl`/`CdRead` naturally misses it even
   though the call exists at runtime.
2. The actual seek is issued by the **kernel executable**
   (`SCUS_941.63`), not `FIELD.BIN` — `FIELD.BIN` only sets shared
   low-memory flags/struct fields (`DAT_80071c1c`, `DAT_8009c6e0`-based
   struct) that a kernel-side movie-service routine polls. This document
   already ruled out an *obvious* hardcoded id-47 branch in the kernel
   exe in an earlier investigation phase, but the **generic** CD-command
   dispatcher was found there (`FUN_8002da7c`, switches on `DAT_8009a000`
   command codes 0x00-0xda) — this was not fully cross-referenced against
   every `DAT_8009a000` write site in the kernel exe for a movie-streaming
   command code, since that search focused on `FIELD.BIN` this session.

### Recommended next step: switch to dynamic tracing

Given static tracing has now exhausted the reachable call graph from the
known opcode handlers without finding a CD call, the highest-value next
step is **dynamic**, not more grep:

- In DuckStation (or another debugger-capable PSX emulator), set a
  breakpoint on `CdControl`/`CdControlB`/`CdRead` (kernel BIOS trap or the
  exe's wrapper `FUN_8002da7c`) during the LOSLAKE1/CANONON cutscene
  trigger, and capture the **call stack** at the moment of the movie seek.
  This directly answers "does `FIELD.BIN` or the kernel exe issue this
  call" and gives the exact caller address in one test, rather than more
  hours of static cross-referencing.
- Alternatively, hardware/software watchpoint on writes to
  `DAT_8009a000` (the CD-command-code global already confirmed in the
  kernel exe) filtered to the movie-streaming command value (likely `0xb`,
  matching the `FUN_80033cb8(0xb, ...)`/`FUN_80033e74` "streaming" mode
  pattern found this session in the kernel exe, called from three
  **walkmap-loading** sites in `FIELD.BIN` — not movie sites — but the
  same command code is plausibly reused for movie streaming) at the
  moment CANONON starts playing.

## Sources

- `workspace/ghidra/FIELD.BIN.dec_disc2.c` (lines 13578-13624: `FUN_800baf54`
  dispatcher; lines 7280-7459: `FUN_800afefc`, the false-lead GTE dispatch)
- `workspace/ghidra/FIELD.BIN.dec_disc2.html` (lines 51100-51330: `pmvie`/
  `movie`/`mvief` handler disassembly and string xrefs; lines 95157-95159:
  `PTR_LAB_800e0228` table entries at `800e0604`-`800e060c`)
