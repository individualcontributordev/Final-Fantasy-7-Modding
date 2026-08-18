# Task: Confirm field 637 CSR changes are back, retest movie audio flicker

## Why

The last build (v0.1.2.1) accidentally deleted 3 bytes' worth of CSR
corrective edits from the Single-disc core layer while I was chasing the
LOSLAKE1/Hojo/ending audio flicker. That deletion is why field 637 lost some
of its CSR changes. I have reverted that deletion (v0.1.2.2), so field 637
should be back to normal.

The movie audio flicker itself is **not fixed yet** — the reference disc
image I was comparing against turns out to have the same flicker bug, so
matching it byte-for-byte was the wrong target. I'm redoing that fix from
first principles. This task is just to confirm the field 637 regression is
gone and get a fresh flicker baseline; expect flicker to still be present.

## What you do

1. Go to https://individualcontributor.dev/builder/. Use the "clear pack
   cache" button at the bottom of the page, then reload once (the pack
   version changed to 0.1.2.2, so this forces a fresh download).
2. Base: CSR
3. Mods: Single-disc only (CSR+ off)
4. Build Disc 1.
5. Quit DuckStation fully if it was already open, then start fresh (no
   cheat engine / speedhack).
6. Load field 637 and check that the CSR changes you noticed missing before
   are present again (describe what you see either way).
7. Load a save near the Bugenhagen waterfall FD scene (Cosmo Canyon, plays
   LOSLAKE1) and play through it, listening for audio flicker/crackle.
8. If you have a save near the Hojo scene at Corel/Junon (Car_1209, plays
   CANONHT2), also test that movie's audio.
9. If reachable, also retest the ending movie audio.

## Evidence (paste)

```
APPLIED single-disc:
APPLIED movies:
CSR+: OFF
Field 637 CSR changes: PRESENT / STILL MISSING / OTHER (describe)
LOSLAKE1 audio: CLEAN / FLICKER / OTHER
Hojo (CANONHT2) audio: CLEAN / FLICKER / OTHER (if tested)
Ending audio: CLEAN / FLICKER / OTHER (if tested)
Load method:
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.
