# Task: Retest disc1-to-disc2 break on single-disc-on-csr v0.1.9

## What was wrong

Field #632 LOSIN2 is end of disc 1 (before the disc-2 ask / BLACKBGB hub).
Single-disc had installed CSR Disc 2 LOSIN2 there. Only CSR Disc 1 LOSIN2
sets GameMoment 0xa455, which opens the LOST2/COS_BTM2 break scene.

Without that: black screen + regular disc 2 music, no break.

## Fix

single-disc-on-csr-v0.1.9 restores CSR D1 LOSIN2.
Keeps CSR D2 LOST2 + COS_BTM2 and BLACKBGB without DSKCG.

## What you do

1. Hard-refresh the builder
2. Base: CSR
3. Mods: Single-disc only (CSR+ off)
4. Confirm APPLIED has single-disc-on-csr-v0.1.9
5. Build Disc 1
6. Quit DuckStation fully; no CE
7. Load in-game save or save-state a field or two before LOSIN2 / transition
8. Run end of disc 1 through break

Expect:
- LOSIN2 behaves like multi-disc CSR disc 1 end (not D2 forest open)
- Break scene/menu like multi-disc CSR after disc 2 swap
- Not black-only with only disc 2 music

Save-states OK only if taken a field or two before the scene under test.

## Evidence (paste)

```
APPLIED single-disc id:
movies pack auto?: YES/NO
LOSIN2 feel: D1 end / D2 open / OTHER
Disc1 to disc2: OK BREAK / BLACK+MUSIC / FREEZE / OTHER
Break scene/menu: YES / NO
Playable after: YES / NO
Load method: in-game save / save-state (field or two before)
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.

Commit example: ops: retest disc1-disc2 break after single-disc 0.1.9
