# Task: Retest field 637 flicker fix + field 643 CSR restore (v0.1.2.3)

## Why

Confirmed your reports were both real, distinct bugs (not stale cache).
Decoded the actual `PMVIE` opcodes and confirmed: field 637 plays
`CANONON.MOV` (cannon scene, matches your report), field 639 plays
`LOSLAKE1.MOV` (waterfall), and field 643 doesn't play a movie at all —
it's the missing CSR script changes there that were the real bug.

1. **Field 637 (CANONON.MOV) flicker** — `single-disc-on-csr` had 3 stray
   byte records that silently reverted the correct Form2 audio-engine
   lengths (set earlier by `manip-movies`) for MOVIE_ID rows 47 (CANONON,
   field 637) and 52 (CANONHT2, Hojo) back to wrong values, right after
   they'd been set correctly. Found this by diffing the *actual applied
   layer stack* end-to-end instead of checking manip-movies' bytes alone
   (the earlier "already correct" conclusion only looked at one layer).
   Removed the 3 records.
2. **Field 643 (WHITE2/Cosmo Canyon) missing CSR changes** — a real CSR
   Disc 2 script edit (a `JMPF` bypass in the post-movie script) got
   silently dropped when the v0.1.4 movie-crawl-avoidance fix rewrote that
   same script from the wrong (pre-merge) source. Rebuilt the script from
   the CSR-edited version with the movie-strip re-applied on top, so both
   fixes are preserved together.

Verified via full rebuild of the entire layer stack + byte-level decode of
`MOVIE_ID.BIN` and the field script (not just diffing against a
possibly-also-broken reference bin, which caused an earlier false fix).
Need your in-game confirmation before calling this closed.

## What you do

1. Open a **private/incognito browser window** (avoid any stale cache).
2. Go to https://individualcontributor.dev/builder/.
3. Base: CSR. Mods: Single-disc only (CSR+ off). Build Disc 1.
4. Quit DuckStation fully if it was already open, then start fresh (no
   cheat engine / speedhack).
5. Load field 637 and trigger the cannon movie (CANONON) — listen for audio
   flicker/crackle.
6. Load field 643 (WHITE2 / Cosmo Canyon) and confirm the CSR script
   changes there are present again.
7. If reachable, also retest the ending movie audio and the Hojo
   (CANONHT2, Car_1209 scene) movie audio — both share the same class of
   fix as field 637.

## Evidence (paste)

```
Used incognito window: YES
APPLIED single-disc:
APPLIED movies:
CSR+: OFF
Field 637 (CANONON) audio: CLEAN / FLICKER / OTHER
Field 643 CSR changes: PRESENT / MISSING / OTHER (describe)
Hojo (CANONHT2) audio: CLEAN / FLICKER / OTHER (if tested)
Ending audio: CLEAN / FLICKER / OTHER (if tested)
Load method:
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.
