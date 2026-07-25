# Makou ISO save path

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Status:** promoted → `docs/02-disc-format.md`  
**Related:** [encounter-rng-architecture](2026-07-25-encounter-rng-architecture.md)

## Summary

Makou Reactor delegates ISO rebuild to **ff7tk**; saving an ISO rewrites modified field files, updates `FIELD.BIN`'s gzip index, and patches ISO9660 directory records.

## Discovery

### Makou layer (`FieldArchiveIOPSIso::save2`)

1. Serialize modified `.DAT` / `.BSX` / `.MIM` → `IsoFile::setModifiedFile()`
2. `iso.pack(&isoTemp, …)` writes `disc.bin.makoutemp`
3. Atomic rename over original

Source: `~/makoureactor/src/core/field/FieldArchiveIOPS.cpp`

### ff7tk layer (`IsoArchive::pack`)

1. Relocate grown files to padding gaps or disc end
2. `IsoArchiveFF7::reorganizeModifiedFilesAfter()` → updates:
   - `FIELD.BIN` (field file LBA/size table)
   - `WORLD.BIN`
   - `INIT/YAMADA.BIN`
3. Stream sectors; `repairLocationSectors()` patches ISO directory

Source: `~/ff7tk/src/formats/IsoArchive.cpp`, `IsoArchiveFF7.cpp`

### FIELD.BIN index update (`updateBin`)

- Decompress gzip → find `(old_lba, old_size)` pairs → replace with new values → recompress
- Field file table search start offset: `0x30000`

### Known limitation

ff7tk does **not** recalculate EDC/ECC sector checksums (`buildFooter` TODO in `IsoArchive.h`).

## Why it matters

After patching `FIELD.BIN`, we can recompress with project scripts and reinsert via the same Makou/ff7tk path.

## Sources

- `~/makoureactor/src/core/field/FieldArchiveIOPS.cpp` lines 332–454
- `~/ff7tk/src/formats/IsoArchiveFF7.cpp` — `updateFieldBin()`, `updateBin()`
