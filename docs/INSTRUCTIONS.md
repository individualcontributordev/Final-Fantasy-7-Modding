# Task: Retest single-disc v0.1.3.1 (fixes D1→D2 corruption from v0.1.3)

## Why

Your playtest of v0.1.3 found: no save prompt on the D1→D2 transition, and
field 634 (the Cosmo Canyon forest, LOST2) was corrupted on load. Root
cause confirmed and fixed:

`bin_diff_to_layer.py` diffed the v0.1.3 merged work bin against **pristine**
Disc 1 instead of against the **CSR base** the builder actually stacks the
layer on top of. Any byte where the merge happened to land back on the
pristine value — but CSR's base layer had already changed that byte —
produced no diff record, so the stale CSR byte silently stayed underneath.
This corrupted three fields badly enough that they fail to parse at all:
`BLACKBGB` (the disc-swap hub — this is why the save prompt vanished, the
field itself was broken, not just missing the Ask), `LOST2` (field 634),
and `NIVGATE`. Three more (`BUGIN1A`, `RCKTIN2`, `RCKTIN7`) had wrong bytes
in a few slots but still parsed.

**Fix (v0.1.3.1):** re-diffed the same merged work bin against the CSR
v0.14.1 base instead of pristine. All 9 rework-merge fields now parse
cleanly and the 6 whole-file fields byte-match their intended CSR D1/D2
source exactly (verified via `field_dat.py` parse + byte-compare). Added
a regression test (`test_rework_fields_parse_and_match_csr_source`) that
would have caught this before shipping.

`verify_builder_config.py` confirms the full 9-addon stack (base +
single-disc-on-csr v0.1.3.1 + manip-movies + 7 endings parts) applies
cleanly: 4,268,702 total records, no conflicts.

## What you do

1. Open a **private/incognito browser window** (avoid any stale cache —
   the builder caches layers by `id@version`, and the version bumped to
   0.1.3.1 specifically so your browser won't reuse the broken 0.1.3 layer).
2. Go to https://individualcontributor.dev/builder/.
3. Base: CSR. Mods: Single-disc only (CSR+ off). Build Disc 1.
4. Check the builder's "applied" list — confirm `single-disc-on-csr` shows
   version `0.1.3.1` (not `0.1.3`).
5. Quit DuckStation fully if it was already open, then start fresh (no
   cheat engine / speedhack).
6. Play through the D1→D2 story break (LOSIN2 → LOST2, near the end of the
   Corel/Rocket Town sequence) — confirm you get the save/disc-change
   prompt, and that field 634 (forest near Cosmo Canyon) now loads
   correctly with music and the break-scene cutscene.
7. Trigger the Supernova (SNOVA) materia/summon in battle — confirm it
   plays and doesn't freeze or garble.
8. Load field 637 and trigger the cannon movie (CANONON) — listen for
   audio flicker/crackle (should be clean, unaffected by this fix).
9. If reachable, play through to the ending and check the credits movies
   play correctly.

## Evidence (paste)

```
Used incognito window: YES
APPLIED single-disc version shown: (should be 0.1.3.1)
D1->D2 save/disc-change prompt: APPEARED / MISSING
Field 634 (LOST2 forest) load: OK / FROZE / OTHER (describe)
D1->D2 break scene cutscene: OK / MISSING / OTHER (describe)
SNOVA/Supernova: OK / FAILED TO TRIGGER / GARBLED
Field 637 (CANONON) audio: CLEAN / FLICKER / OTHER
Ending/credits movies: PLAYED / MISSING / OTHER (describe)
Load method:
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.
