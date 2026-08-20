# Per-slot edit-origin (pristine-anchored) for 9 rework fields

| Field | Slot | D1 edited by CSR? | D2 edited by CSR? | Origin verdict |
|---|---|---|---|---|
| BLACKBGB (field #103) | init:0 | True | True | Identical CSR edits (byte rearrangement only) -> take CSR D1 |
| BUGIN1A | AD:4 | True | False | D1-ONLY edit -> take D1 |
| BUGIN1A | AD:7 | False | True | D2-ONLY edit -> take D2 |
| BUGIN1A | BUGEN:1 | True | False | D1-ONLY edit -> take D1 |
| COS_BTM | BUGEN:3 | True | False | D1-ONLY edit -> take D1 |
| COS_BTM | BUGEN:31 | True | False | D1-ONLY edit -> take D1 |
| COS_BTM | MES:31 | True | False | D1-ONLY edit -> take D1 |
| COS_BTM2 | AD:0 | True | True | D1 superset of D2 edit -> take D1 |
| COS_BTM2 | BALLET:1 | True | True | D1 superset of D2 edit -> take D1 |
| COS_BTM2 | BALLET:6 | True | False | D1-ONLY edit -> take D1 |
| COS_BTM2 | BALLET:7 | True | False | D1-ONLY edit -> take D1 |
| COS_BTM2 | BUGEN:3 | True | False | D1-ONLY edit -> take D1 |
| COS_BTM2 | CLOUD:22 | True | False | D1-ONLY edit -> take D1 |
| COS_BTM2 | EARITH:1 | True | True | D1 superset of D2 edit -> take D1 |
| COS_BTM2 | EARITH:7 | True | False | D1-ONLY edit -> take D1 |
| COS_BTM2 | EARITH:30 | True | True | no pristine baseline (slot missing pre-CSR) |
| COS_BTM2 | KETCY:6 | True | False | D1-ONLY edit -> take D1 |
| COS_BTM2 | RED:1 | True | True | D1 superset of D2 edit -> take D1 |
| COS_BTM2 | TIFA:1 | True | True | D1 superset of D2 edit -> take D1 |
| COS_BTM2 | TIFA:8 | True | False | D1-ONLY edit -> take D1 |
| COS_BTM2 | YUFI:8 | True | False | D1-ONLY edit -> take D1 |
| DEL1 | border1:2 | True | False | D1-ONLY edit -> take D1 |
| DEL1 | crew2:3 | True | False | D1-ONLY edit -> take D1 |
| DEL1 | earith:7 | True | False | D1-ONLY edit -> take D1 |
| DEL1 | tifa:7 | True | False | D1-ONLY edit -> take D1 |
| DEL1 | yufi:31 | True | False | D1-ONLY edit -> take D1 |
| JUNAIR2 | dir:0 | True | False | D1-ONLY edit -> take D1 |
| LOST2 | Info:4 | False | True | D2-ONLY edit -> take D2 |
| LOST2 | ballet:3 | False | True | D2-ONLY edit -> take D2 |
| LOST2 | ballet:5 | False | True | D2-ONLY edit -> take D2 |
| LOST2 | cefir:31 | False | True | D2-ONLY edit -> take D2 |
| LOST2 | cid:3 | False | True | D2-ONLY edit -> take D2 |
| LOST2 | cid:5 | False | True | D2-ONLY edit -> take D2 |
| LOST2 | cloud:7 | False | True | D2-ONLY edit -> take D2 |
| LOST2 | cloud:31 | False | True | D2-ONLY edit -> take D2 |
| LOST2 (field #634) | init:0 | True | True | D2 adds missing MAPJUMP to COS_BTM2 (field #526) -> take D2 |
| LOST2 | ketcy:3 | False | True | D2-ONLY edit -> take D2 |
| LOST2 | ketcy:5 | False | True | D2-ONLY edit -> take D2 |
| LOST2 | line:3 | False | True | D2-ONLY edit -> take D2 |
| LOST2 | red13:3 | False | True | D2-ONLY edit -> take D2 |
| LOST2 | red13:5 | False | True | D2-ONLY edit -> take D2 |
| LOST2 | tifa:3 | False | True | D2-ONLY edit -> take D2 |
| LOST2 | tifa:5 | False | True | D2-ONLY edit -> take D2 |
| LOST2 | version:0 | False | True | no pristine baseline (slot missing pre-CSR) |
| LOST2 | version:31 | False | True | no pristine baseline (slot missing pre-CSR) |
| LOST2 | vincent:3 | False | True | D2-ONLY edit -> take D2 |
| LOST2 | vincent:5 | False | True | D2-ONLY edit -> take D2 |
| LOST2 | yufi:3 | False | True | D2-ONLY edit -> take D2 |
| LOST2 | yufi:5 | False | True | D2-ONLY edit -> take D2 |
| NIVGATE | b_drct:1 | False | True | D2-ONLY edit -> take D2 |
| NIVGATE | b_drct:31 | False | True | D2-ONLY edit -> take D2 |
| NIVGATE | cefiros:3 | True | False | D1-ONLY edit -> take D1 |
| NIVGATE | cefiros:6 | False | True | D2-ONLY edit -> take D2 |
| NIVGATE | cefiros:7 | False | True | D2-ONLY edit -> take D2 |
| NIVGATE | cloud:3 | True | False | D1-ONLY edit -> take D1 |
| NIVGATE | cloud:11 | False | True | D2-ONLY edit -> take D2 |
| NIVGATE | cloud:13 | False | True | D2-ONLY edit -> take D2 |
| NIVGATE | cloud:17 | False | True | D2-ONLY edit -> take D2 |
| NIVGATE | hei1:3 | True | False | D1-ONLY edit -> take D1 |
| NIVGATE | hei1:31 | False | True | D2-ONLY edit -> take D2 |
| NIVGATE | hei2:3 | True | False | D1-ONLY edit -> take D1 |
| NIVGATE | hei2:31 | False | True | D2-ONLY edit -> take D2 |
| NIVGATE | line_jp:2 | True | False | D1-ONLY edit -> take D1 |
| NIVGATE | tifa:1 | False | True | D2-ONLY edit -> take D2 |
| NIVGATE | tifa:5 | False | True | D2-ONLY edit -> take D2 |
| NIVGATE | tifa:9 | False | True | D2-ONLY edit -> take D2 |
| NIVGATE | zax:5 | False | True | D2-ONLY edit -> take D2 |
| RCKTIN2 | cid:1 | True | False | D1-ONLY edit -> take D1 |
| RCKTIN2 | leader:0 | False | True | D2-ONLY edit -> take D2 |

## Notes on judgement calls

### LOST2 (field #634), init:0

Both discs edit this slot but not the same way, so it isn't a simple
superset like COS_BTM2. Decoded comparison:

- **Pristine D1/D2** (identical): `MPNAM -> IFUB -> MUSIC -> JMPF -> MUSIC -> RET -> IFUB -> REQ -> AKAO x12 -> RET`
- **CSR D1**: adds an `IFUW addr=0x0020 != 0xa455` gate around both `MUSIC`
  calls (skip replaying music once Game Moment 0xa455 is already set).
  Nothing else changes.
- **CSR D2**: adds the same `IFUW` gate around the music (with `AKAO2`
  calls added too), **plus** a block CSR D1 completely lacks:
  ```
  IFUW addr=0x0020 == 0xa455, else +0xb
  MAPJUMP field #526 (COS_BTM2)
  IFSW
  REQ
  IFUB
  REQ
  ```

This `MAPJUMP field #526 (COS_BTM2)` is the Cosmo Canyon break scene
transition. It directly matches the open bug in
`docs/reference/disc-transition-knowledge-base.md` — single-disc
currently uses CSR D1's version of this slot, which lacks this jump,
so the break scene never plays and LOST2 (field #634) has no music.

**Verdict: take CSR D2.** It's a superset of D1's music-guard edit, plus
the missing disc-transition logic single-disc needs.
