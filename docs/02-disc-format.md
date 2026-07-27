# Disc Format and Save Path

## Final Fantasy VII PS1 disc layout (relevant parts)

```
disc.bin (Mode 2 / 2352-byte sectors)
└── FIELD/
    ├── FIELD.BIN    ← field engine + file index (gzip compressed)
    ├── *.DAT        ← per-map scripts, walkmesh, encounters
    ├── *.MIM        ← backgrounds
    └── *.BSX        ← field models
```

Square bypassed the ISO9660 30-file directory limit with a custom index inside
`FIELD.BIN`.

## FIELD.BIN structure

1. **8-byte GZIPPS header**
   - Bytes 0–3: decompressed size (uint32 LE)
   - Bytes 4–7: gzip sub-header (preserve on recompress)
2. **Gzip payload** — decompress to get engine code + data tables

Inside decompressed data (from Qhimm research):

| Offset (approx) | Content |
|-----------------|---------|
| `0x3A5B8` | LBA + size pairs for every field file |
| Throughout | Field engine MIPS code, opcode tables, RNG table |

## Makou Reactor save flow (ISO mode)

Source: `makoureactor/src/core/field/FieldArchiveIOPS.cpp`

1. Serialize modified `.DAT` / `.BSX` / `.MIM` into memory
2. `iso.pack()` → writes `disc.bin.makoutemp`
3. ff7tk updates `FIELD.BIN` index if file positions/sizes changed
4. Patches ISO9660 directory records
5. Renames temp file over original

**We will use the same reinsert path** after patching `FIELD.BIN` manually.

## Tools for FIELD.BIN replacement

| Tool | Use |
|------|-----|
| Project scripts | Decompress / recompress GZIPPS (`decompress_gzipps.py` / `compress_gzipps.py`) |
| Makou Reactor | Open ISO, save ISO (after manual FIELD.BIN swap) |
| CDmage / CDProg | Alternative: import single file at same LBA |
| ff7tk `IsoArchive` | Programmatic pack (used by Makou internally) |

## EDC/ECC note

ff7tk does **not** recalculate sector EDC/ECC on save. Emulators usually tolerate
this; real hardware may be pickier. CDmage can fix checksums if needed.

## Workspace file naming

```
workspace/pristine/            Retail masters — never open for CDmage import
├── FINALFANTASY7_D1.bin … D3.bin (+ .cue)

workspace/iso-extract/         Disposable working copies only
├── FINALFANTASY7_DN.bin       Copied from pristine, then CDmage import (auto-save OK)
├── FIELD.BIN                  Extracted from working disc
├── FIELD.BIN.dec              Decompressed (Ghidra input)
└── FIELD.BIN.new              Recompressed, ready to import
```

CDmage auto-saves on import into the open file. Keep a clean vault under `pristine/`; only open copies in `iso-extract/`. No Save As required.
