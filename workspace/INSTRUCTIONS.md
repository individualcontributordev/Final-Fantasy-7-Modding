# Task: build + test the JUNAIR precision-patch .bin

Found why Field 384 stopped loading entirely: the JUNAIR precision patch
only copied CSR D2's `air0/3` script slot but silently dropped a 1-byte
text-table entry D2 also added in the same edit, corrupting JUNAIR.DAT's
text section. Fixed `fix_junair_air0_slot3.py` to splice in D2's whole
text table too -- verified byte-identical to CSR D2's JUNAIR.DAT now.
Retest the original battle-return freeze repro.

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
