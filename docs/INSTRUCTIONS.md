# Task: Retest LOSLAKE1 and Hojo (CANONHT2) movie audio for flicker

## Why

The movie video was already playing correctly, but the sound flickered on
the ending movie and/or LOSLAKE1 (Bugenhagen waterfall). Root cause: the
Single-disc core layer was quietly reverting a fix that made those two
movies' engine data (used for audio timing) correct, so the game was mixing
in leftover audio data from the wrong stream. That revert is now removed.

## What you do

1. Hard-refresh the builder page (clear cache so it re-downloads the layer
   files, not just reload):
   - Open DevTools > Application > Clear storage > Clear site data, or
   - Ctrl+Shift+R / Cmd+Shift+R a few times.
2. Go to https://individualcontributor.dev/builder/
3. Base: CSR
4. Mods: Single-disc only (CSR+ off)
5. Build Disc 1.
6. Quit DuckStation fully if it was already open, then start fresh (no
   cheat engine / speedhack).
7. Load a save near the Bugenhagen waterfall FD scene (Cosmo Canyon, the
   scene that plays the lake/waterfall FMV) and play through it. Listen
   closely to the audio for flicker/crackle.
8. If you have a save near the Hojo scene at Corel/Junon (Car_1209, plays
   CANONHT2), also test that movie's audio.
9. If reachable, also retest the ending movie audio.

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
