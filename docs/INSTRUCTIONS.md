# Task: Playtest single-disc-on-csr v0.2.4 (fixes WHITE2 #643 movie hang)

## Why

Cosmo Canyon's WHITE2 (field 643) plays two short movies as part of its
script. On the single-disc build those movies no longer point at valid
movie data at that location on the disc, so the game hangs when it
tries to play them (screen freezes/glitches, no progress).

Fix: the movie-playing part of that field's script has been removed.
The scene now fades to black and continues, instead of trying to play
the broken movies.

Also removed a leftover one-byte patch in LOST2 (#634): a diagnostic
build proved it does nothing on this game — the field before LOST2
already sets things up so LOST2's condition is already true, so the
patch had no effect on the D1→D2 break scene either way. Removing it
does not change how the game plays.

Bumped to **v0.2.4**. This is a fresh playtest — confirm the D1→D2
transition/music/Makou-save fixes from v0.2.3 still hold, and that
WHITE2 no longer hangs.

The build isn't committed (`.bin`/`.cue` gitignored) — rebuilt locally
below.

## Prerequisites

- `workspace/pristine/FINALFANTASY7_D1.bin`, `_D2.bin`, `_D3.bin` present.
- `Final-Fantasy-7-CSR` repo checked out as a sibling of this repo.
- Python 3 on PATH; run all commands from this repo's root.

## What you do

1. `git pull --ff-only`.
2. Rebuild the work bin and a matching `.cue`:

   ```bash
   python3 mods/single-disc/scripts/build_work_bin.py -o workspace/iso-extract/single-disc-v024-repro.bin
   printf 'FILE "single-disc-v024-repro.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > workspace/iso-extract/single-disc-v024-repro.cue
   ```

   Expect a line `FIELD/WHITE2.DAT ... removed IFSW/PMVIE/JMPF/PMVIE/MOVIE
   block` during the "Fixing WHITE2 movie hang" step. No `WARNING:` or
   uncaught errors.

3. Open `workspace/iso-extract/single-disc-v024-repro.cue` in
   DuckStation fresh (no save states, no cheats).
4. New game, play through Midgar to confirm baseline sanity (no hangs).
5. Progress to the Disc 1→2 transition (BLACKBGB field #103 → LOST2 →
   break scene → COS_BTM2). Confirm it still goes straight to the break
   scene with music, and LOST2's background still renders correctly
   (unchanged from v0.2.3).
6. Reach Cosmo Canyon and enter WHITE2 (the field with the
   character-lock / camera-movie moment). Confirm:
   - The scene fades to black and continues normally (fixed), or
   - The game freezes/glitches trying to play a movie (bug still
     present).
7. Open this bin in Makou Reactor, make a trivial edit, Save. Confirm
   it still succeeds (should be unchanged from v0.2.3).

## Evidence (paste)

```
Disc 1->2 transition: straight to break scene with music (expected)
LOST2 background: renders correctly (expected)
WHITE2: fades to black and continues (fixed) / freezes or glitches (bug)
Makou save test: SUCCEEDED / FAILED (paste exact text)
notes:
```

## When done

Paste evidence above, commit this file, push, say check.
