# Task: playtest FSHIP_12 (67) -> MD8_5 (731) movie fix

Root cause of "field 67 jumps straight to 731 without playing any movies":
FSHIP_12's `ad` entity Script 2 (called from `drctr`'s init via REQEW, so
it IS live -- confirmed with a CFG trace, not just opcode-presence
scanning) plays 3 movies (`PMVIE`/`MOVIE` pairs) right before REQ'ing
Script 3, which does the ASK + `MAPJUMP` to field 731 (MD8_5). Those 3
movie ids are `0x3b` (59), `0x32` (50), `0x33` (51) -- **unchanged from
retail pristine D1/D2 and CSR D1**, i.e. this is not a single-disc
regression but a genuine multi-disc mechanic: on retail multi-disc this
scene only ever played correctly with Disc 2 inserted.

On single-disc's D1-only 54-row `MINT/MOVIE_ID.BIN` table:
- id 59 was completely **out of bounds** (table only has rows 0-53) --
  the PMVIE call for it does nothing, silently.
- id 50 resolved to `EARITHDD.MOV` (wrong).
- id 51 resolved to `FUNERAL.STR` (wrong, and not even a movie -- a still
  frame).

CSR D2's own table resolves the same 3 ids to the Highwind/Junon-cannon
CANONHT triplet (`CANONHT1.MOV`/`CANONHT2.MOV`/`CANONH1P.MOV`), matching
your hypothesis about CANONHT2. Fixed by repointing D1 ids 50/51 to CSR
D2's CANONHT1/CANONHT2 (EOF append, larger sources) and growing
`MOVIE_ID.BIN` to 60 rows for a new id 59 -> CANONH1P.MOV (engine-table
row only, no ISO9660 dirent needed -- PMVIE resolves purely through this
table). No field script bytes changed. Shipped as a new delta layer
`single-disc-csr-manip-movies-v0.1.6` (applies after v0.1.5, before
nothing else) and wired into `build_playtest_bin.py`.

1. Pull and rebuild the playtest .bin (repo root, your machine):
   ```bash
   cd "$(git rev-parse --show-toplevel)"
   git pull --ff-only
   python3 mods/single-disc/scripts/build_playtest_bin.py
   ```
   Writes `workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.bin` / `.cue`.
2. Open the `.cue` in DuckStation.
3. Play field 67 (FSHIP_12) to the point that leaves toward field 731
   (MD8_5), game moment 1600 -- the CANONHT1/CANONHT2/CANONH1P movie
   sequence should now play before the transition, and MD8_5 should load
   with characters correctly positioned in bounds (no more logic break).
4. Re-check field 673 (CANONON, moment 1566) and the world-map freezes
   (fields 347/71, moments 1568/1580) still work -- both are on the same
   build pipeline, quick re-confirm only.
5. Tell me: did the movies play and did MD8_5 load correctly, and any new
   fields/transitions that still break (name + game moment).

---

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
