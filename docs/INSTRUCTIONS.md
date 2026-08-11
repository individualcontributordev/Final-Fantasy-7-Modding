# Task: Retest disc1-to-disc2 break on single-disc-on-csr v0.1.8

## What was wrong

v0.1.6/0.1.7 forced LOST2 MAPJUMP to cos_btm2 and opened COS_BTM2 gates.
That is NOT the multi-disc CSR path. Forced land on cos_btm2 with normal
GameMoment hits IFSW GM >= 0x202 then RET = black screen + music, no break.

CSR multi-disc break still OK (swap D2, stay on D2 LOST2).

## Fix

single-disc-on-csr-v0.1.8 restores pure CSR Disc 2 LOST2 + COS_BTM2
(no force). BLACKBGB still has DSKCG stripped and sets disc id 2.

## What you do

1. Hard-refresh the builder
2. Base: CSR
3. Mods: Single-disc only (CSR+ off)
4. Confirm APPLIED has single-disc-on-csr-v0.1.8
5. Build Disc 1
6. Quit DuckStation fully; no CE
7. Load in-game save or save-state a field or two before the transition
8. Run disc1-to-disc2 / break

Expect: same as multi-disc CSR break (menu/scene + music), not black-only

Save-states OK only if taken a field or two before the scene under test.

## Evidence (paste)

```
APPLIED single-disc id:
movies pack auto?: YES/NO
Disc1 to disc2: OK BREAK / BLACK+MUSIC / FREEZE / OTHER
Break scene/menu: YES / NO
Playable after: YES / NO
Load method: in-game save / save-state (field or two before)
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.

Commit example: ops: retest disc1-disc2 break after single-disc 0.1.8
