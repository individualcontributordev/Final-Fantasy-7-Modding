# Task: Retest disc1-to-disc2 break on single-disc-on-csr v0.1.7

## What was wrong

CSR multi-disc break OK. CSR + Single-disc (no CSR+) still: black screen + music, no break.

Cause: LOST2 already forced MAPJUMP to cos_btm2 (v0.1.6), but COS_BTM2 gates the break
on disc-id IFUW. Single-disc never sets disc=2, so the else branch skips the scene.

Fix: single-disc-on-csr-v0.1.7 clears those IFUW else-jumps on COS_BTM2.

## What you do

1. Hard-refresh the builder
2. Base: CSR
3. Mods: Single-disc only (CSR+ off)
4. Confirm APPLIED has single-disc-on-csr-v0.1.7
5. Build Disc 1
6. Quit DuckStation fully; no CE
7. Load in-game save or save-state a field or two before the transition
8. Run disc1-to-disc2 / break

Expect: break / cos_btm2 like multi-disc CSR

## Evidence (paste)

```
APPLIED single-disc id:
movies pack auto?: YES/NO
Disc1 to disc2: OK BREAK / BLACK+MUSIC / FREEZE / OTHER
Break / cos_btm2: YES / NO
Playable after: YES / NO
Load method: in-game save / save-state (field or two before)
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.

Commit example: ops: retest disc1-disc2 break after single-disc 0.1.7
