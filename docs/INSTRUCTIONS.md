# Task: build + test the JUNAIR precision-patch .bin

Fixed a bug in field_dat_write.py: NIVGATE has two different entities
both named "b_drct", and the aliased-slot conflict check matched edits
by name only, wrongly treating the unrelated entity's aliased group as
edited too. Now resolves the specific ScriptSlot object, not just the
name. Build succeeds again -- retest the battle-return freeze.

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
