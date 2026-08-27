# Task: playtest the full single-disc build (VRAM-base fix applied)

Root-caused and fixed the freeze after battle-return on Field 384 (Junon
airfield, JUNAIR.DAT): `write_field_dat()` was recomputing every
FIELD/*.DAT's internal VRAM section-pointer header using a hardcoded base
address instead of that field's actual load address (e.g. JUNAIR loads at
0x80115000, not 0x80000000). This corrupted the pointer header on every
precision-patched field (JUNAIR, WHITE2, BUGIN1A, NIVGATE, RCKTIN2,
DSKCG-removal) -- the file still loaded but internal pointers were wrong,
causing a black-screen hang instead of a clean failure. Fixed generically
(uses each field's own `vbase`, confirmed no other script hardcodes a
base) and rebuilt the **full** single-disc-on-csr v0.2.12 stack, not just
JUNAIR in isolation.

Requires `workspace/pristine/FINALFANTASY7_D1.bin` (and D2, D3 if not
already present) in place on your machine first.

1. Build the .bin yourself (run this from the repo root on your machine):
   ```bash
   cd "$(git rev-parse --show-toplevel)"
   git pull --ff-only
   python3 mods/single-disc/scripts/build_work_bin.py -o workspace/iso-extract/sd_full_test.bin
   ```
2. Make a matching .cue next to it (same folder), containing exactly:
   ```
   FILE "sd_full_test.bin" BINARY
     TRACK 01 MODE2/2352
       INDEX 01 00:00:00
   ```
   Save as `workspace/iso-extract/sd_full_test.cue`.
3. Open `sd_full_test.cue` in DuckStation.
4. Play to Field 384 (Junon airfield), trigger a battle, and return from
   it (moment 1016) -- this is the original freeze repro.
5. Tell me: did it freeze, freeze differently, or load fine?
6. Known pre-existing cosmetic issue (not a regression, present in
   reference build too): during the elevator sequence, some background
   tiles ("squares") are missing from the static background. This is
   deprioritized -- don't worry about reporting it again unless it's
   changed.
7. If Field 384 is clean, continue playtesting broadly (D1->D2 transition
   via BLACKBGB, a few other battle-returns) to confirm the VRAM-base fix
   didn't regress anything else, since it touched 6 fields' patch logic.
