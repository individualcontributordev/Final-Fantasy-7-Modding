# Task: playtest with FIELD.BIN corruption fix (Field 347/71 world-map freeze)

Root cause of the Field 347 (fr_e, Diamond Weapon fight) and Field 71
(fship_24, Hojo scene) freezes you reported when loading from the world map
(moments 1568/1580): both `.DAT` files themselves were byte-identical to
the working reference bin, so the field scripts were never the problem.
The actual bug was in `FIELD/FIELD.BIN` -- the engine's embedded
(location,size) lookup table for every field file -- which was silently
**corrupted** by the previously-shipped `builder/single-disc-on-csr/layers/disc1.layer.json`
layer: applying it produced a `FIELD.BIN` gzip payload that failed to
decompress (`invalid literal/length/distance code`, truncated ~3.7 KB short
of the expected 264008-byte table). Any field whose table entry landed in
or after the truncated region could hang the engine on load, even though
its own `.DAT` was intact -- consistent with only some world-map-loaded
fields freezing while others worked.

Confirmed by rebuilding fresh via `build_work_bin.py` (which re-runs the
merge + `fix_field_bin_table.py` recompression from scratch): the rebuilt
`FIELD.BIN` decompresses cleanly to the full 264008 bytes. Re-diffed that
rebuild against the CSR base into a fresh `disc1.layer.json` and confirmed
applying it reproduces the rebuilt bin byte-for-byte. Replaced the broken
committed layer with this fixed one.

1. Pull and rebuild the playtest .bin (repo root, your machine):
   ```bash
   cd "$(git rev-parse --show-toplevel)"
   git pull --ff-only
   python3 mods/single-disc/scripts/build_playtest_bin.py
   ```
   Writes `workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.bin` / `.cue`.
2. Open the `.cue` in DuckStation.
3. Re-check Field 347 (Diamond Weapon fight, moment 1568) and Field 71
   (Hojo/Highwind scene, moment 1580) loading from the world map -- both
   should now load without freezing.
4. Re-check Field 673 (CANONON movie, moment 1566) still plays correctly --
   this fix only touches FIELD.BIN's table, not the movie layers, but worth
   a quick re-confirm since it's the same build pipeline.
5. Continue broad playtesting, including JUNAIR (field 384, Gelnica movie)
   and TRNAD_51 (field 706, train-scene variants).
6. Tell me: did 347 and 71 load correctly now, and any other fields that
   still freeze on load (world-map or field-to-field) -- if so, name the
   field id/name and game moment so I can check whether it also fell in
   FIELD.BIN's corrupted table region or is a separate issue.
