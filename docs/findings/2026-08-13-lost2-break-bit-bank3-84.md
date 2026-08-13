# LOST2 disc-break gate: bank3[0x84] bit4

**Date:** 2026-08-13  
**Pack:** single-disc-on-csr-v0.1.29  

## Symptom

After D1→D2 transition on single-disc: straight to LOST2 #634 forest, no break
scene (COS_BTM2 #526), no music.

## Root cause

CSR D2 LOST2 init (correct IF compare types, FFRTT fail-at-E semantics):

| GM | bit bank3/0x84#4 | Result |
|----|------------------|--------|
| 0xa455 | clear | IFUB fail → IFUW `!=` a455 fails → **RET** (no MUSIC, no MAPJUMP) |
| 0xa455 | set | IFUB OK → path leads to **MAPJUMP #526** COS_BTM2 |
| other | clear | AKAO2 resume + MUSIC, stay on 634 |

LOSIN2 (D1 break) sets GameMoment `0xa455` and **BITOFF** `83308404` (clears
bit4). LOSINN is the field that **BITON** `82308404` (sets it). BLACKBGB LOST2
paths never set bit4 after Ask-strip removes DSKCG.

v0.1.27 (JMPF AKAO2) and v0.1.28 (force IFUW else=0 / COS_BTM2 open) did not
set the gate. Forcing COS_BTM2 with GM≥0x0202 blacks the scene (v0.1.8).

## Fix

On Ask-stripped BLACKBGB, before each MAPJUMP #634, same-length 10-byte swap:

```
WAIT 04 + WAIT 08 + BITON 0x89#1
→ BITON 0x84#4 + BITON 0x89#1 + JMPF 0
```

Restore pure CSR D2 LOST2 + COS_BTM2.

## Sim

- a455 + bit4 → MJ526  
- a455 + no bit → RET  

## Superseded

v0.1.29 BITON approach caused black/glitch on playtest. Restored v0.1.8/0.1.9
path in **v0.1.30** (pure CSR D2 LOST2/COS_BTM2 + Ask BLACKBGB, no BITON84).
See CHANGELOG 0.1.8 / 0.1.30.
