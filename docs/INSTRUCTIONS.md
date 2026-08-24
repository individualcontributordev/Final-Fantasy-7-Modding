# Extract + Ghidra-search FIELD.BIN / BATTLE.X from all 3 discs

## Why

Static search on **Disc 1**'s `FIELD.BIN`/`BATTLE.X` for the hardcoded
ENDING01/ENDING3E/ENDING2E/CANONON seek LBAs found nothing. That's expected:
CANONON's trigger lives in D2's `LOSLAKE1` field script, and the true
ending sequence lives in D3's `LAS4_0`/ending fields — neither of those
scripts exist on D1. Re-run the same searches, but pull `FIELD.BIN` (and
`BATTLE.X`, in case it's a shared table there) from pristine **Disc 2**
and pristine **Disc 3** instead, since that's where this code natively
lives and was never modified.

Pristine images already exist at:

```
workspace/pristine/FINALFANTASY7_D1.bin
workspace/pristine/FINALFANTASY7_D2.bin
workspace/pristine/FINALFANTASY7_D3.bin
```

## 1. Extract compressed FIELD.BIN + BATTLE.X from each disc

Run from repo root (`cd "$(git rev-parse --show-toplevel)"`):

```bash
mkdir -p workspace/iso-extract/multi-raw workspace/iso-extract/multi-dec

python3 << 'PY'
from pathlib import Path
from scripts.psx_mode2_iso import extract_file

out = Path("workspace/iso-extract/multi-raw")
for disc in (1, 2, 3):
    img = bytearray(Path(f"workspace/pristine/FINALFANTASY7_D{disc}.bin").read_bytes())
    for name in ("FIELD.BIN", "BATTLE/BATTLE.X"):
        data = extract_file(img, name)
        tag = name.split("/")[-1]
        dest = out / f"D{disc}_{tag}"
        dest.write_bytes(data)
        print(f"wrote {dest} ({len(data)} bytes) head={data[:12].hex()}")
PY
```

You should get 6 files: `D1_FIELD.BIN`, `D1_BATTLE.X`, `D2_FIELD.BIN`,
`D2_BATTLE.X`, `D3_FIELD.BIN`, `D3_BATTLE.X`. All heads should show `1f8b`
starting at byte offset 8 (GZIPPS marker).

## 2. Decompress each one

```bash
cd "$(git rev-parse --show-toplevel)"
for f in workspace/iso-extract/multi-raw/*; do
  name=$(basename "$f")
  python3 scripts/decompress_gzipps.py "$f" "workspace/iso-extract/multi-dec/${name}.dec"
done
```

This produces `D1_FIELD.BIN.dec`, `D1_BATTLE.X.dec`, `D2_FIELD.BIN.dec`,
`D2_BATTLE.X.dec`, `D3_FIELD.BIN.dec`, `D3_BATTLE.X.dec` in
`workspace/iso-extract/multi-dec/`.

## 3. Import each into Ghidra

For **each** of the 6 `.dec` files, create a new Ghidra import (can be
separate programs in the same project):

| Setting | Value |
|---------|-------|
| Format | Raw Binary |
| Language | MIPS: R3000 32bit little endian |
| Base address (FIELD.BIN) | `0x800A0000` |
| Base address (BATTLE.X) | `0x800A0000` |

After importing, run Analyze → yes to defaults (MIPS analysis) on each.

## 4. Search for the hardcoded LBAs

For **D2's FIELD.BIN/BATTLE.X** (CANONON only — LOSLAKE1 lives on D2) and
**D3's FIELD.BIN/BATTLE.X** (all three ENDING ids — the ending fields live
on D3), use **Search → For Scalars** (or Search → Memory, decimal/hex as
needed) for the relevant values below, one at a time. Try both decimal and
hex forms — Ghidra's scalar search usually takes decimal by default.

D1's copies are just there for a baseline diff if needed — the D1 search
already came up empty and isn't expected to change.

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

Paste, for each of the 4 values (CANONON against D2, the 3 ENDING ids
against D3): found / not found, and if found, the address + whether it
looked like code or a table entry (with nearby bytes if it's a table).

## Fallback if D2/D3 search also comes up empty: live trace

D1's `FIELD.BIN.dec`/`BATTLE.X.dec` were already searched (raw bytes and
decompiled text, as 32-bit words LE/BE and as MSF triples plain/BCD) —
**no hits anywhere**, which is expected since D1 doesn't contain these
scripts. If the D2/D3 search above also comes up empty, static search is a
dead end and the next step is a **live breakpoint in DuckStation** on the
actual CD-ROM seek, to capture the return address (the calling code) at
the moment it fires.

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
