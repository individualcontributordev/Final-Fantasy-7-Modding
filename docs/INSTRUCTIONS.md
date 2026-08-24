# Find hardcoded ending/CANONON seek LBAs

## Status

`FIELD.BIN`/`BATTLE.X` are byte-identical across D1/D2/D3 (confirmed by
MD5) — shared engine overlays, ruled out, nothing more to do there.

The hardcoded seek must be in one of:
- Per-field script bytecode for `LOSLAKE1` (D2, CANONON trigger) or the
  ending field(s) (D3)
- The main `SCUS_941.63` executable

## Task: extract + Ghidra-search the .DAT scripts and SCUS executable

1. Extract + decompress the field `.DAT` files via `scripts/lzs.py` (not
   `decompress_gzipps.py`) — see `docs/02-disc-format.md` for the FIELD.DAT
   format:
   - `LOSLAKE1` from pristine `workspace/pristine/FINALFANTASY7_D2.bin`
   - The ending field(s) from pristine `workspace/pristine/FINALFANTASY7_D3.bin`
     (check `docs/01-encounter-system.md` or the field name list for the
     exact ending field ID — likely `LAS4_0` or similar)
2. Extract `SCUS_941.63` raw from `workspace/pristine/FINALFANTASY7_D1.bin`
   (not GZIPPS-compressed, use `extract_file` directly, no decompress step).
3. Import each into Ghidra:
   - Field `.DAT` bytecode: base address per `docs/02-disc-format.md` FIELD.DAT layout
   - `SCUS_941.63`: base `0x80010000`, after its 0x800-byte header (per `docs/ghidra-battle-overlays.md`)
4. **Search → For Scalars**, decimal and hex, one at a time:

| Movie    | Decimal  | Hex        |
|----------|----------|------------|
| ENDING01 | `163608` | `0x27F18`  |
| ENDING3E | `172631` | `0x2A257`  |
| ENDING2E | `197242` | `0x3027A`  |
| CANONON  | `250450` | `0x3D252`  |

For each hit: note whether it's in code (instruction operand, e.g. part of
a `lui`/`ori`/`li` pair) or data (table entry — check for a repeating
stride like the SNOVA table's 8-byte `lba, padded_size` entries).

## Report back

For each of the 4 values: found / not found, and if found — which file,
the address, and code vs. table entry (with nearby bytes if it's a table).

## Fallback if this also comes up empty: live trace in DuckStation

1. **Settings → Advanced → Enable Debugging Tools** (or launch with
   `-debugger`). Restart if prompted.
2. Load a built single-disc image that reaches `LOSLAKE1`/CANONON (faster
   to reach than the true ending, same seek mechanism).
3. Open the Debugger window (Debug menu → CPU Debugger).
4. Add a memory **write** breakpoint at `0x1F801802` (CD-ROM parameter
   FIFO — a `Setloc` writes 3 MSF bytes here before the command byte hits
   `0x1F801801`).
5. Resume, play up to the CANONON lake scene. The breakpoint may fire many
   times (normal file-read seeks use this path too) — Continue until the
   3 bytes just written decode to MSF `(55, 41, 25)` (CANONON) or one of
   the ENDING MSF triples above.
6. At that hit, check the debugger's call stack / return address ($ra/r31)
   — that's the calling function. Note the address (`0x8xxxxxxx` range).

Report: whether the breakpoint fired on the right MSF, the return address,
and if call stack isn't exposed, the current PC + a short disassembly
window (10-15 instructions) around it.
