# Per-slot edit-origin (pristine-anchored) for 9 rework fields

| Field | Slot | D1 edited by CSR? | D2 edited by CSR? | Origin verdict |
|---|---|---|---|---|
| BLACKBGB | init:0 | True | True | BOTH edited independently -> needs judgement call |
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
| LOST2 | init:0 | True | True | BOTH edited independently -> needs judgement call |
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
