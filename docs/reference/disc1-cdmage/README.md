# Disc 1 File Structure (CDmage Screenshots)

Complete file listing of pristine FF7 PSX Disc 1 with LBA addresses and sizes, captured from CDmage.

## Images

1. **[01-root-directories.png](01-root-directories.png)** — Root directory structure
   - Shows top-level folders: FIELD, ENEMY, INIT, MENU, MINT, MOVIE, STAGE, WIPE, etc.
   - Key files with LBAs:
     - `BIGEXIT.MOV` @ LBA 18054,272
     - `MOVIE.BIN` @ LBA 2582,200
     - `CAR_1329.STR` @ LBA 21375,065
     - Various `.MOV` files (opening, endings, FMVs)
     - Various `.STR` files (field movie streams)

2. **[02-field-files.png](02-field-files.png)** — FIELD directory contents
   - Shows all `FIELD/*.DAT` files (map scripts) with LBAs
   - Each field has multiple columns showing different file instances/versions
   - Critical for single-disc mod: these DAT files contain `DSKCG` (Ask-for-disc) opcodes that must be removed

3. **[03-additional-files.png](03-additional-files.png)** — Additional game files
   - Shows files in directories like:
     - `MOVIE/*.DAT` (movie engine files)
     - `MENU/*.DAT` (menu system)
     - Various character/location files (`MCxxx`, `MTxxx`, etc.)
     - `TUNNEL/*.DAT`, `UTAI/*.DAT`, etc.

## Use Cases

### Single-Disc Mod Development

These screenshots are essential for:

1. **Ask-for-disc removal** — Identifying which `FIELD/*.DAT` files need `DSKCG` opcode removal
2. **SNOVA LBA patching** — Finding files that reference Disc 3 LBAs that need remapping to Disc 1
3. **Movie relocation** — Planning where to append Disc 2/3 movies onto Disc 1 (must stay under ~80min CD limit)
4. **File size verification** — Checking if files will fit when moved to Disc 1

### Layer Building

When building `ic-layer-v1` patches:
- LBA values help calculate byte offsets: `byte_offset = LBA * 2352`
- File sizes help validate patch sizes
- Directory structure helps organize operations by file path

## Related

- **Scripts:** `mods/single-disc/scripts/` — build tools that use this data
- **Ghidra metadata:** `scripts/ghidra/*-functions.json` — code-level analysis
- **Disc format docs:** `docs/02-disc-format.md`

## Notes

- Images captured from pristine US PSX Disc 1 (SCUS-94163)
- All LBAs are for Mode2/2352 sector format
- CD limit: ~333,000 LBAs for 74-minute CD, ~358,000 for 80-minute CD-R
