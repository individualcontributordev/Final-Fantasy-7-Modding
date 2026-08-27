# Task: build + test the JUNAIR precision-patch .bin

Found the real bug (bigger than the last fix): `write_field_dat()` was
recomputing every FIELD/*.DAT's internal VRAM section-pointer header using
a hardcoded base address instead of that field's actual load address
(e.g. JUNAIR loads at 0x80115000, not the assumed 0x80000000). This
corrupted the pointer header on every precision-patched field (JUNAIR,
WHITE2, BUGIN1A, NIVGATE, RCKTIN2, DSKCG-removal) -- the file still loaded
(hence field 384 showing as current) but all internal pointers were wrong,
causing a black-screen hang instead of a clean failure. Fixed to preserve
the original base; rebuilt JUNAIR.DAT is now byte-identical to CSR D2's.
Retest the original battle-return freeze repro (and general field-loading
across the build, since this affected 6 fields, not just JUNAIR).

1. In a terminal (repo root):
   ```
   python3 mods/single-disc/scripts/build_work_bin.py -o workspace/iso-extract/junair-test.bin
   ```
2. Make a matching .cue next to it (same folder), containing exactly:
   ```
   FILE "junair-test.bin" BINARY
     TRACK 01 MODE2/2352
       INDEX 01 00:00:00
   ```
   Save as `workspace/iso-extract/junair-test.cue`.
3. Open `junair-test.cue` in DuckStation.
4. Play to Field 384 (Junon), trigger a battle, and return from it
   (moment 1016) -- same repro as before.
5. Tell me: did it freeze the same way, freeze differently, or not
   freeze at all?
