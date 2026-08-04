# Finding: Loading a save asks for disc 2 on single-disc D1 pack

**Date:** 2026-08-04
**Status:** expected for D2-marked saves; field Ask removal does not cover this

## Report

Burned single-disc 0.1.0 Clean D1: on **load save**, game asks for disc 2.

## What 0.1.0 already changes

Applied layer vs pristine:

| File | Changed? | Role |
|------|----------|------|
| FIELD/BLACKBGB.DAT | yes | Story Ask-for-disc hub |
| FIELD/BLACKBG3.DAT | yes | Ask sites |
| FIELD/BLACKBGE.DAT | yes | Ask disc 2 |
| MINT/DISKINFO.CNF | **no** | Still DISK0001 |
| MENU/SAVEMENU.MNU | **no** | Unmodified |
| FIELD/DSCHANGE.X | **no** | Same as retail |

So **field DSKCG removal is in the pack**. Title / new game / early field already passed on console.

## Why load can still ask for disc 2

FF7 saves store which disc the file belongs to. On Load, the menu/kernel checks that
the inserted medium matches the save (via disc id / DISKINFO path), **before** field
scripts run. That is separate from blackbgb Ask-for-disc.

Typical cases:

1. Save was created on **retail disc 2** (or a D2 image) → load on D1-only pack asks for disc 2
2. Save is midgame with disc slot = 2 even if you never burned D2 no-swap
3. Field hub asks are already stripped — this is **not** losin2 jump Ask if it happens at the save list / after confirm load

## Workarounds (playtest)

1. Use a **Disc 1 save** (or save on this no-swap D1 pack after playing past D1-only content)
2. Hex/editor: set save block disc number to 1 (community save tools / MemcardRex-type editors often expose disc)
3. DuckStation: load state from within session after beginning on D1 new game, instead of card load of D2 file

## Possible pack fixes (later)

| Fix | Notes |
|-----|--------|
| Document only | Ship as "D1 saves only" for Clean single-disc |
| Spoof always DISK0001 already true | Does not rewrite the **save** disc field |
| Patch SAVEMENU / load path to ignore save disc id | Needs RE; correct for full no-swap |
| Provide a tiny "save disc id = 1" utility note | Operator-side |

## Not the same bug

- Missing FMV crawl (movie Set/Play) — separate
- Supernova — separate
- blackbgb Ask during **story disc change** — should already be gone; if Ask appears **on the field after load**, note map name

## Next

Confirm with operator: Ask appears on **save list / load confirm** vs **after entering a field**.
If save UI: need menu/kernel ignore disc on load.
If field: which map — recheck that DAT for remaining DSKCG.
