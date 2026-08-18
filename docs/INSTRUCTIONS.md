# Task: Cache-proof retest of field 637/643 + fresh flicker baseline

## Why

Your last test reported field 643 CSR changes missing and field 637 flicker
still present. I diffed the **live CDN file** you'd actually be downloading
against the repo fix byte-for-byte — they're identical, and both field 643
(WHITE2) and field 637's CSR bytes are present in that file right now. So
the content on the CDN is correct; what you saw was almost certainly a
stale browser cache (IndexedDB) that the "clear pack cache" button missed,
possibly because it was clicked before GitHub Pages finished publishing.

Separately, I derived the correct Form2 audio-engine length for the two
flicker movies **from the actual FMV file sizes** (not by diffing against
any existing disc image, which was the mistake last time):

- Hojo `CANONHT2.MOV`: correct Form2 length is 5,977,824 bytes. The current
  `manip-movies` pack already writes exactly this — should already be
  flicker-free.
- Bugenhagen waterfall `LOSLAKE1.MOV`: correct Form2 length is 6,912,224
  bytes. The current pack instead writes 17,190,624 — clearly wrong (not
  even a multiple of the Form2 sector size). This is almost certainly your
  remaining flicker source. Not fixed yet — need your test below before I
  touch it, so I have a clean before/after.

## What you do

1. Open a **private/incognito browser window** (this guarantees no stale
   IndexedDB cache — don't rely on the "clear pack cache" button this time).
2. Go to https://individualcontributor.dev/builder/.
3. Base: CSR
4. Mods: Single-disc only (CSR+ off)
5. Build Disc 1.
6. Quit DuckStation fully if it was already open, then start fresh (no
   cheat engine / speedhack).
7. Load field 637 and check the CSR changes are present.
8. Load field 643 (WHITE2 / Cosmo Canyon) and check the CSR changes are
   present.
9. Load a save near the Bugenhagen waterfall FD scene (Cosmo Canyon, plays
   LOSLAKE1) and play through it, listening for audio flicker/crackle.
10. If you have a save near the Hojo scene (Car_1209, plays CANONHT2), also
    test that movie's audio — this one should already be clean.
11. If reachable, also retest the ending movie audio.

## Evidence (paste)

```
Used incognito window: YES
APPLIED single-disc:
APPLIED movies:
CSR+: OFF
Field 637 CSR changes: PRESENT / MISSING / OTHER (describe)
Field 643 CSR changes: PRESENT / MISSING / OTHER (describe)
LOSLAKE1 audio: CLEAN / FLICKER / OTHER
Hojo (CANONHT2) audio: CLEAN / FLICKER / OTHER (if tested)
Ending audio: CLEAN / FLICKER / OTHER (if tested)
Load method:
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.
