# Ghidra search: find hardcoded ending/CANONON seek LBAs

## Why

ENDING01/ENDING3E/ENDING2E and CANONON all ignore `MOVIE_ID.BIN` patches at
runtime (confirmed by a failed earlier playtest — table was patched,
DuckStation still sought the original LBA). This matches the already-solved
SNOVA0-15 / LASBOSS3 pattern in BATTLE.X: a raw `(lba, padded_size)` pair
baked directly into decompressed code, bypassing the table entirely. We
want to find out if the same is true here, so the LBA could be patched in
place like SNOVA/LASBOSS3 instead of requiring the payload to sit at the
original absolute LBA on disc.

## What to do

You have `FIELD.BIN.dec` open in Ghidra. If you also have `BATTLE.X`
loaded, check both.

Use **Search → For Scalars** (or Search → Memory, decimal/hex as needed)
for each of these four values, one at a time. Try both decimal and hex
forms — Ghidra's scalar search usually takes decimal by default.

| Movie    | Decimal  | Hex        |
|----------|----------|------------|
| ENDING01 | `163608` | `0x27F18`  |
| ENDING3E | `172631` | `0x2A257`  |
| ENDING2E | `197242` | `0x3027A`  |
| CANONON  | `250450` | `0x3D252`  |

For each search:

1. Note whether you get **any hits** at all.
2. For each hit, note whether it's in **code** (looks like an instruction
   operand, e.g. part of a `lui`/`ori`/`li` pair) or in **data** (sits in a
   `.data`/`.rodata`-looking block, possibly next to a size value).
3. If it's in a data table, look at the surrounding bytes — is there a
   repeating stride (like the SNOVA table's 8-byte `lba, padded_size`
   entries)? Note the address and a few bytes before/after.

## Report back

Paste, for each of the 4 values: found / not found, and if found, the
address + whether it looked like code or a table entry (with nearby bytes
if it's a table).

## Update: static search came up empty — live trace instead

Searched the exported `FIELD.BIN.dec.bin`/`BATTLE.X.dec.bin` (raw bytes)
and `.dec.c` (decompiled text) for all 4 LBAs as 32-bit words (LE/BE) and
as MSF triples (plain + BCD) — **no hits anywhere**. The decompiled C is
also fully unnamed (`FUN_xxxxx`/`DAT_xxxxx`, no "movie" strings), so there's
no textual anchor to chase the normal `MOVIE_ID.BIN` lookup path either.

Static search is a dead end. Next step is a **live breakpoint in
DuckStation** on the actual CD-ROM seek, to capture the return address
(the calling code) at the moment it fires.

### Setup

1. In DuckStation: **Settings → Advanced → Enable Debugging Tools** (or
   launch DuckStation with the `-debugger` flag). Restart DuckStation if
   prompted.
2. Load `workspace/iso-extract/ff7_d1_singledisc_endings_test.cue` (or
   whichever built single-disc image reaches `LOSLAKE1`/CANONON — that
   scene is faster to reach than the true endgame ending, and uses the
   same hardcoded-seek mechanism, so it's a good stand-in to test first).
3. Open the **Debugger** window (Debug menu → CPU Debugger, or similar —
   exact menu wording varies by DuckStation version).

### Set the breakpoint

CD-ROM MMIO command/parameter registers on the PSX sit at
`0x1F801800`-`0x1F801803`. A `Setloc` command works by writing the 3 MSF
bytes to the parameter FIFO (`0x1F801802`) before the command byte hits
the command register (`0x1F801801`). We want to catch the parameter write:

1. In the Debugger window, add a new **memory breakpoint**:
   - Address: `0x1F801802`
   - Type: **Write**
2. Resume execution and play up to the CANONON lake scene (or the ending
   sequence, if testing that directly).
3. When the breakpoint hits, it may fire many times (normal file-read
   seeks also use this path) — you may need to **Continue** several times
   until you're at the specific seek for this scene. Cross-check by
   reading the 3 bytes just written — they should decode to MSF
   `(55, 41, 25)` for CANONON, or one of the ENDING MSF triples from the
   table above.
4. Once you're at the right hit, check the debugger's **call stack /
   return address ($ra / r31)** pane — that address is the actual
   game-code function issuing this seek. Note it down (it'll be a
   `0x8xxxxxxx`-range address).

### Report back

- Whether the breakpoint fired and you found the hit matching CANONON's
  (or an ending's) MSF triple.
- The return address / calling function address at that hit.
- If DuckStation's UI doesn't expose call stack directly, instead note
  the **current PC** at the breakpoint hit, plus a short disassembly
  window (10-15 instructions) around it — screenshot or copy-paste text
  is fine.
