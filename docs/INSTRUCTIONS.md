# Task: Retest single-disc v0.1.3.2 (fixes field 103/BLACKBGB jump corruption)

## Why

Your v0.1.3.1 playtest found field 103 (BLACKBGB) still broken — Makou
Reactor showed opcodes like "Forward 87 byte(s)" instead of "Goto label X",
meaning a jump instruction's target no longer lands on a real instruction.
Root cause confirmed and fixed:

`remove_dskcg.py` deleted DSKCG ("Ask for disc") opcode bytes from a script
slot but never fixed up the byte offsets encoded in the jump/if opcodes
(`JMPF`, `JMPFL`, `JMPB`, `JMPBL`, `IFUB`, `IFUBL`, `IFSW`, `IFSWL`, `IFUW`,
`IFUWL`, `IFKEY`, `IFKEYON`, `IFKEYOFF`, `IFPRTYQ`, `IFMEMBQ`) elsewhere in
the same slot. Those opcodes encode their target as a byte count relative
to their own position; deleting bytes shifts everything after them, so any
jump whose source or target moved landed on the wrong byte. `BLACKBGB` has
4 DSKCG removed (most of any field), so it broke worst, but `BLACKBGE` (1)
and `BLACKBG3` (14) had the same latent bug.

**Fix (v0.1.3.2):** `remove_dskcg_from_script` now remaps every surviving
jump/if opcode's offset against the compacted script as DSKCG ops are
dropped. Verified all 974 jump/if opcodes across the 12 rework/DSKCG fields
in the full stack resolve to real instruction boundaries (0 bad, previously
unverified). Field layouts checked against Makou Reactor's own `Opcode.h`/
`Opcode.cpp` source in this repo.

`verify_builder_config.py` confirms the full 9-addon stack (base +
single-disc-on-csr v0.1.3.2 + manip-movies + 7 endings parts) applies
cleanly: 4,268,672 total records, no conflicts.

## What you do

1. Open a **private/incognito browser window** (avoid any stale cache —
   version bumped to 0.1.3.2 so your browser won't reuse the broken layer).
2. Go to https://individualcontributor.dev/builder/.
3. Base: CSR. Mods: Single-disc only (CSR+ off). Build Disc 1.
4. Check the builder's "applied" list — confirm `single-disc-on-csr` shows
   version `0.1.3.2` (not `0.1.3.1`).
5. In Makou Reactor, open the built bin → FIELD folder → `BLACKBGB.DAT` →
   Field editor → Script editor. Confirm every jump opcode shows
   "Goto label N" (or "If ... Goto label N"), never a raw "Forward N
   byte(s)"/"Back N byte(s)". Spot-check `BLACKBGE.DAT` and `BLACKBG3.DAT`
   the same way.
6. Quit DuckStation fully if it was already open, then start fresh (no
   cheat engine / speedhack).
7. Play through the D1→D2 story break (LOSIN2 → LOST2, near the end of the
   Corel/Rocket Town sequence) — confirm you get the save/disc-change
   prompt, and that field 634 (forest near Cosmo Canyon) loads correctly
   with music and the break-scene cutscene.
8. Trigger the Supernova (SNOVA) materia/summon in battle — confirm it
   plays and doesn't freeze or garble.
9. Load field 637 and trigger the cannon movie (CANONON) — listen for
   audio flicker/crackle (should be clean, unaffected by this fix).
10. If reachable, play through to the ending and check the credits movies
    play correctly.

## Evidence (paste)

```
Used incognito window: YES
APPLIED single-disc version shown: (should be 0.1.3.2)
BLACKBGB.DAT in Makou: all jumps show "Goto label N" / STILL SHOWS "Forward N byte(s)"
BLACKBGE.DAT / BLACKBG3.DAT spot-check: OK / BAD (describe)
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
