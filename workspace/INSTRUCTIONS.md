# Task: playtest the full single-disc build WITH manip-movies (CANONON fix)

Root cause of the missing Junon Cannon movie you reported (field 673
move_r / LOSLAKE1, moment 1566, jairofal/cannonon scene): the `.bin` you
were testing (`sd_full_test.bin`) was built with
`build_work_bin.py`, which only runs the raw CSR-field-script merge
pipeline. It never applies the **manip-movies** layers
(`single-disc-csr-manip-movies-v0.1.4`/`v0.1.5`) that alias CSR D2's
CANONON.MOV onto D1's hardcoded LOSLAKE1 CD-seek (ISO LBA 250450) and
relocate/repoint several other CSR-D2-only movies (GELNICA, C_SCENE1,
C_SCENE3, FF_DAIKU). Field script content for move_r/LOSLAKE1 was never
missing or wrong -- the movie *asset* was just never installed into that
build. Confirmed by rebuilding with the correct pipeline
(`build_playtest_bin.py`): JAIROFAL.MOV's ISO content == CSR D2's
CANONON.MOV byte-for-byte, and the LBA 250450 raw sector matches D2's
CANONON sector0 (Form2 submode 0x42) -- both verified programmatically
before writing the .bin.

Requires `workspace/pristine/FINALFANTASY7_D1.bin` and
`FINALFANTASY7_D2.bin` in place on your machine first.

1. Build the .bin yourself (run this from the repo root on your machine):
   ```bash
   cd "$(git rev-parse --show-toplevel)"
   git pull --ff-only
   python3 mods/single-disc/scripts/build_playtest_bin.py
   ```
   This writes both the `.bin` and a matching `.cue` for you already:
   `workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.bin` /
   `.cue`. Do NOT use `sd_full_test.bin` or `build_work_bin.py`'s output
   for playtesting anymore -- those never include the manip-movies layer
   stack and will always be missing CANONON/GELNICA/C_SCENE1/C_SCENE3.
2. Open `ff7_d1_playtest_csr_sd_movies.cue` in DuckStation.
3. Re-check field 673 (move_r / LOSLAKE1, moment 1566) -- the Junon
   Cannon (CANONON) movie should now play.
4. Play to Field 384 (Junon airfield), trigger a battle, and return from
   it (moment 1016) -- this was a previously-fixed freeze repro, confirm
   still clean on this build.
5. Tell me: did CANONON play, and did Field 384 load fine?
6. Known pre-existing cosmetic issue (not a regression): during the
   elevator sequence, some background tiles ("squares") are missing from
   the static background. Deprioritized -- no need to re-report unless
   it's changed.
7. Continue playtesting broadly, including JUNAIR (field 384, Gelnica
   movie) and TRNAD_51 (field 706, all GameMoment-gated train-scene
   variants) since those also depend on the manip-movies relocation step
   this build now includes.
