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
