# CANONON hardcode: not found in SCUS_941.63 (kernel exe) — negative result

## Question

Does the engine special-case PMVIE id 47 (CANONON) specifically, or a
broader pattern, when it bypasses `MOVIE_ID.BIN`? See
`docs/findings/2026-08-24-canonon-hardcode-clean-room-reverification.md`
for the confirmed live-test finding this follows up on.

## What was searched

Full decompiled C export of `SCUS_941.63` (Disc 1 kernel executable,
36,671 lines, `workspace/ghidra/SCUS_941.63_disc1.c`, gitignored/local):

- **Hypothesis A (hardcoded filename string)**: grep for `CANONON` —
  **zero hits** anywhere in the file. Also zero hits for other movie
  stems (`GELNICA`, `RCKTOFF`, `NRCRL`).
- **Hypothesis B (hardcoded/computed LBA, literal id check)**:
  - Found the one and only reference to `MOVIE_ID.BIN` at line 16517,
    inside `FUN_80034f5c` — this function just opens the file, seeks via
    `CdControlB(2, ...)`, and streams it into a fixed buffer
    (`DAT_8009a1f4`, 0x80 bytes) via `FUN_80041d28`/`FUN_80041e30`. It
    does **not** index into the loaded table by movie id, and does not
    reference the movie id at all — it reads the *whole file* into RAM,
    presumably for another routine to index later. That indexing routine
    was **not found** in this executable.
  - Searched for a comparison against literal `47`/`0x2f` anywhere
    near CD-seek code, PMVIE-adjacent code, or the table-open routine:
    no hits. The three `0x2f` occurrences in the file are all unrelated
    (an unrelated threshold check, an offset add in a text-render
    routine, and a byte-scaling multiply).
  - `case 0xf8:` at line 11542 (`FUN_80026c5c`) looked promising at
    first (0xf8 = PMVIE opcode value) but is a **false lead**: that
    function indexes `DAT_800707c0`, a bitmap-font glyph-width table, by
    a raw byte value in a text-rendering/window-sizing routine. `0xf8`
    there is coincidental — an escape/control byte in that routine's own
    switch, unrelated to field-script opcode dispatch or movies.
  - No field-script opcode dispatcher (i.e., the actual `case`-per-PMVIE
    style switch that would call into a movie-id → LBA resolver) exists
    in `SCUS_941.63` at all.

Also checked `workspace/ghidra/FIELD.BIN.dec.c` (18,760 lines, an
existing decompile of `FIELD.BIN`, the field-script container) for
`PMVIE`, `MOVIE`, `0xf8`, `CdControl`, `CdRead`, `MOVIE_ID`: **zero
hits**. This decompile is likely of a different/generic field overlay
function set, not the movie-trigger code path, or Ghidra's auto-analysis
didn't resolve enough of it to produce recognizable strings/calls.

## Conclusion

**The CANONON-specific branch is not present in `SCUS_941.63`.** The
kernel executable's only `MOVIE_ID.BIN`-reading function
(`FUN_80034f5c`) is a generic bulk-load with no id-based branching
visible in the decompile. This means either:

1. The special case is genuinely elsewhere — most likely inside
   `FIELD.BIN`'s CANONON field script itself (a field-script-level
   hardcoded seek/LBA rather than an engine-kernel-level one), which
   would explain why patching the table row does nothing: the field
   script for that scene may issue its own direct CD seek instead of
   going through the generic PMVIE→table path for this one scripted
   sequence, OR
2. Ghidra's decompiler failed to recover the relevant function (e.g. it
   got folded into an unnamed/unlabeled function, or the analysis pass
   used for the export was incomplete — Auto Analyze not fully finished
   before export).

Both remain open. Given zero signal in the kernel exe, the productive
next step is **not** more grepping of `SCUS_941.63`, but checking
CANONON's own field script (`.BIN` file, likely `fielddir`-listed field
matching the cannon-town scene) for a hardcoded seek instruction that
bypasses the generic PMVIE opcode handling — i.e. check whether this
field's script issues `PMVIE 47` at all, or does something else
entirely (a different opcode, or a raw CD-control call baked into the
script). This shifts the investigation from "kernel special-cases id 47"
to "this field's own script hardcodes the movie," which is a different
and more tractable hypothesis given the tools already in this repo
(`scripts/`, `docs/01-encounter-system.md`-adjacent field-script
parsing).

## Status of the open question

Not answered. Downgrading from "is this a broader engine pattern?" to:
**re-scope to field-script level, not kernel-executable level.**
