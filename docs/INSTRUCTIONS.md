# Task: Playtest Single-disc v0.2.0 fresh rebuild (fields only, no movies/endings)

## Why

The single-disc mod had stability regressions in v0.1.3+. We scrapped that
history and rebuilt from scratch using the Aug 7 "99% stable" logic as the
reference: CSR Disc 1 base, with Disc 2/Disc 3 field data merged in (9-field
verdict-table rework merge + 66-field safe bulk merge), all 19 "Ask for
disc" (DSKCG) ops removed from the 3 disc-swap fields, and SNOVA (the
overworld save-point model set) copied from Disc 3 onto Disc 1 with the
hardcoded LBAs in `BATTLE.X` remapped to match.

Manip-movies and the ending-credits packs are **disabled** for this pass —
this is a fields-only test of the new merge/DSKCG/SNOVA core before movies
get layered back on top. `single-disc-on-highwind` is untouched (still
disabled from before).

`verify_builder_config.py` confirms the base+addon stack applies cleanly
(155,148 total records) and the resulting bytes are confirmed identical to
the source-built work bin.

## What you do

1. Open a **private/incognito browser window** (avoid stale cache).
2. Go to https://individualcontributor.dev/builder/.
3. Base: CSR (v0.14.1). Mods: **Single-disc** only — do not enable CSR+
   scene add-ons for this test. Build Disc 1.
4. Confirm the builder's "applied" list shows `single-disc-on-csr` at
   **v0.2.0** and does **not** show any `manip-movies` or `ending credits`
   packs (they should be absent/disabled).
5. Boot the built Disc 1 image fresh in DuckStation (no cheats/speedhack).
6. Play a normal early-game sequence to confirm baseline sanity:
   - New game intro through Midgar reactor 1 bombing mission loads fine.
   - Enter/exit a few field screens without hangs or corrupted graphics.
7. Head to a location or two known to hit **merged-in D2/D3 fields**
   (e.g. Junon area, Cosmo Canyon, or wherever LOST2/COS_BTM/COS_BTM2/
   DEL1/JUNAIR2/BUGIN1A/NIVGATE/RCKTIN2 fields are reachable) — confirm no
   crashes, no missing/garbled field geometry or scripts.
8. Try to trigger a former disc-swap point (any of the 3 DSKCG fields:
   BLACKBGB, BLACKBGE, BLACKBG3) — confirm the game **does not** ask for a
   disc swap and continues seamlessly.
9. If you reach a scene that would normally load an overworld save point
   (SNOVA), confirm it renders correctly (this tests the SNOVA D3→D1
   inject + BATTLE.X LBA remap).
10. Note anything unexpected: freezes, black screens, wrong field data,
    corrupted movies (movies aren't merged yet, so vanilla-disc1 behavior
    there is expected/OK for this pass).

## Evidence (paste)

```
Used incognito window: YES
Applied version shown for single-disc-on-csr: (should be 0.2.0)
manip-movies/endings shown as applied: (should be NONE)
Intro -> reactor 1 bombing mission: OK / FROZE / OTHER
Field navigation (few screens): OK / GLITCHED / OTHER
D2/D3 merged field(s) visited (name which): OK / BROKEN / OTHER
DSKCG field triggered (name which, if any): NO HANG / STILL ASKS FOR DISC / OTHER
SNOVA save point (if reached): OK / BROKEN / N/A
Load method:
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.
