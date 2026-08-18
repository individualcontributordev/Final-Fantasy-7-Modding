# Task: Retest LOSLAKE1 and Hojo (CANONHT2) movie audio for flicker

## Why

The movie video was already playing correctly, but the sound flickered on
the ending movie and/or LOSLAKE1 (Bugenhagen waterfall). Root cause: the
Single-disc core layer was quietly reverting a fix that made those two
movies' engine data (used for audio timing) correct, so the game was mixing
in leftover audio data from the wrong stream. That revert is now removed.

## What you do

1. Go to https://individualcontributor.dev/builder/ (plain reload is fine
   now — the Single-disc pack version was bumped to 0.1.2.1, which forces
   your browser to fetch the fixed layer instead of using a stale cached
   copy). If you still see old audio behavior, use the "clear pack cache"
   button at the bottom of the page and reload once.
2. Base: CSR
3. Mods: Single-disc only (CSR+ off)
4. Build Disc 1.
5. Quit DuckStation fully if it was already open, then start fresh (no
   cheat engine / speedhack).
6. Load a save near the Bugenhagen waterfall FD scene (Cosmo Canyon, the
   scene that plays the lake/waterfall FMV) and play through it. Listen
   closely to the audio for flicker/crackle.
7. If you have a save near the Hojo scene at Corel/Junon (Car_1209, plays
   CANONHT2), also test that movie's audio.
8. If reachable, also retest the ending movie audio.

## Evidence (paste)

```
APPLIED single-disc:
APPLIED movies:
CSR+: OFF
LOSLAKE1 audio: CLEAN / FLICKER / OTHER
Hojo (CANONHT2) audio: CLEAN / FLICKER / OTHER (if tested)
Ending audio: CLEAN / FLICKER / OTHER (if tested)
Load method:
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.
