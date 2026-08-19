# Task: Identify the waterfall field + cache-proof retest of 637/643

## Why

I decoded the actual `PMVIE` (play-movie) opcodes baked into the field
scripts, instead of guessing from field/movie names (which was wrong last
time — field *names* like "loslake1" don't necessarily match the movie
they play). Facts, straight from the CSR field scripts:

- **Field 637** (internal field name `loslake1`) calls `PMVIE id=47` →
  that resolves to **`CANONON.MOV`** — a cannon scene. This matches what
  you described field 637 as ("cannon movie").
- **Field 639** (internal field name `loslake3`) calls `PMVIE id=57` →
  that resolves to **`LOSLAKE1.MOV`** — the actual waterfall FMV file.
- **Field 643** (internal field name `white2`, Cosmo Canyon) calls PMVIE
  three times, for `FALLPL.MOV`, `WHITE2.BIN`, and `C_SCENE2.MOV` — **none
  of these is `LOSLAKE1.MOV`**. So field 643 doesn't appear to play the
  waterfall movie at all in the CSR base.

This means my working theory (waterfall plays on field 643) is likely
wrong, and field 639 is the actual candidate. I need you to confirm which
field number you're actually on when you see the Aeris-face/waterfall
scene before I touch `MOVIE_ID.BIN` again — get it wrong and I'll "fix"
a movie/field that was never broken, like last time.

Separately, I found the **correct Form2 audio-engine length for
`LOSLAKE1.MOV`**, read directly from Disc 2's own `MINT/MOVIE_ID.BIN`
table (not derived/guessed): **6,912,224 bytes**. The current
`manip-movies` pack in this repo instead writes 17,190,624 for that slot —
clearly wrong (not even a Form2-sector multiple). That's almost certainly
a real flicker source, but I want to confirm the field number above before
patching it.

Hojo `CANONHT2.MOV`'s already-baked-in engine length (5,977,824) matches
Disc 2's own table exactly, so that one row is correct.

## What you do

1. Open a **private/incognito browser window** (guarantees no stale
   IndexedDB cache from earlier tests).
2. Go to https://individualcontributor.dev/builder/.
3. Base: CSR. Mods: Single-disc only (CSR+ off). Build Disc 1.
4. Quit DuckStation fully if it was already open, then start fresh (no
   cheat engine / speedhack).
5. Get to the Bugenhagen waterfall scene (Aeris' face, Cosmo Canyon area)
   and, using Makou Reactor or an in-game field indicator/debug tool (or
   just describe exactly what room/screen it is — which NPCs, what's
   nearby), tell me the **field name or number** so I can cross-check it
   against field 639/643.
6. Load field 637 and check the CSR changes are present.
7. Load field 643 (WHITE2 / Cosmo Canyon) and check the CSR changes are
   present.
8. Listen for audio flicker/crackle during the waterfall scene itself.
9. If reachable, also retest the ending movie audio.

## Evidence (paste)

```
Used incognito window: YES
APPLIED single-disc:
APPLIED movies:
CSR+: OFF
Waterfall/Aeris-face scene — field name or number (or detailed description):
Field 637 CSR changes: PRESENT / MISSING / OTHER (describe)
Field 643 CSR changes: PRESENT / MISSING / OTHER (describe)
Waterfall scene audio: CLEAN / FLICKER / OTHER
Ending audio: CLEAN / FLICKER / OTHER (if tested)
Load method:
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.
