# Task: build + test the JUNAIR precision-patch .bin

JUNAIR.DAT is no longer swapped wholesale from CSR D2 -- only the one
script slot CSR actually changed (air0/3) is patched now. Build the
merged single-disc core .bin fresh and retest the battle-return freeze.

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
