# Task: Playtest single-disc v0.1.3 (rebuilt field merge + restored movies/endings)

## Why

v0.1.3 replaced the old hand-audited field-merge lists with an automated
rebuild (9-field rework merge + 66-field safe bulk merge + DSKCG removal +
SNOVA inject). While publishing it we also found and fixed two manifest
bugs left over from the old v0.1.2 whole-bin-diff approach:

1. Stale `single-disc-v0.1.2-part2..10` auto-includes were still stacking
   old v0.1.2 bytes on top of the new v0.1.3 layer — now disabled.
2. `single-disc-csr-manip-movies-v0.1.4` (Form2 MOVIE_ID audio-flicker fix
   + LOSLAKE1 waterfall alias) and `single-disc-endings-v0.1.0-part1..7`
   (ending/credits movies) had been silently dropped from auto-applying
   with Single-disc on CSR since that same v0.1.2 changeover — now
   restored to auto-apply with `single-disc-on-csr`.

`verify_builder_config.py` confirms the full 9-addon stack (base +
single-disc-on-csr + manip-movies + 7 endings parts, 4,360,412 total
records) applies cleanly with no conflicts. This has **not** been
runtime-tested yet.

## What you do

1. Open a **private/incognito browser window** (avoid any stale cache).
2. Go to https://individualcontributor.dev/builder/.
3. Base: CSR. Mods: Single-disc only (CSR+ off). Build Disc 1.
4. Check the builder's "applied" list — confirm it shows only
   `single-disc-on-csr` (no `single-disc-v0.1.2-part2..10` entries), plus
   the hidden manip-movies/endings layers auto-applying underneath.
5. Quit DuckStation fully if it was already open, then start fresh (no
   cheat engine / speedhack).
6. Play through the D1→D2 story break (LOSIN2/LOST2 area near the Corel
   Rocket Town / Junon sequence) — confirm the break-scene cutscene fires
   correctly without a real disc swap.
7. Trigger the Supernova (SNOVA) materia/summon in battle — confirm it
   plays and doesn't freeze or garble.
8. Load field 637 and trigger the cannon movie (CANONON) — listen for
   audio flicker/crackle (should be clean, this was already fixed).
9. If reachable, play through to the ending and check the credits movies
   play correctly on the single-disc build (this is newly restored — has
   not been confirmed working since v0.1.2).

## Evidence (paste)

```
Used incognito window: YES
APPLIED single-disc: (paste exact list shown by builder)
APPLIED movies/endings shown as applied: YES / NO
Old v0.1.2 part2-10 NOT shown as applied: CONFIRMED / STILL SHOWING
D1->D2 break scene (LOST2): OK / FROZE / OTHER (describe)
SNOVA/Supernova: OK / FAILED TO TRIGGER / GARBLED
Field 637 (CANONON) audio: CLEAN / FLICKER / OTHER
Ending/credits movies: PLAYED / MISSING / OTHER (describe)
Load method:
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.
