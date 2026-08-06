# Field compare: csr:D1:DEL1 vs csr:D2:DEL1

**Classification:** `scripts` (meaningful)

| | csr:D1:DEL1 | csr:D2:DEL1 | delta |
|--|--:|--:|--:|
| compressed | 21432 | 21456 | 24 |
| decompressed | 42436 | 42512 | 76 |
| script slots | 106 | 106 | |
| text entries | 69 | 69 | |
| text padding | 2 | 2 | 0 |

## Sections

- `scripts`: 12356 → 12432 (**DIFF**)
- `walkmesh`: 12516 → 12516 (same)
- `background`: 16584 → 16584 (same)
- `camera`: 56 → 56 (same)
- `inf`: 740 → 740 (same)
- `encounter`: 48 → 48 (same)
- `model_loader`: 108 → 108 (same)

Scripts identical: **False** (5 differing slots)
Text content identical: **True** (diff ids: [])
AKAO identical: **True**

## Script `border1` slot 2

bytes 81 → 65

```diff
--- csr:D1:DEL1
+++ csr:D2:DEL1
@@ -2,12 +2,9 @@
 MENU2 4a01
 AKAO f20000002a00c000000000000000
 REQSW 0207ca
-JMPF 100f
 AKAO f2000000c1280000000000000000
 FADE 6b0000000000080200
 SCR2DC 660000b3ff42003c00
 SCRLW 67
-BITON 8230e000
-MAPJUMP 60bb01bafaa6fd820078
+MAPJUMP 60ba0100000000000000
 RET 00
-MAPJUMP 60ba0100000000000000
```

## Script `crew2` slot 3

bytes 51 → 51

```diff
--- csr:D1:DEL1
+++ csr:D2:DEL1
@@ -1,5 +1,6 @@
 SCR2D 6400c8ff4300
-SCR2DC 660000c8ff11004000
+WAIT 243c00
+SCR2DC 660000c8ff11008000
 REQSW 0209c5
 WAIT 243c00
 REQSW 020ac5
@@ -12,4 +13,3 @@
 REQEW 0307c6
 JMPB 1200
 RET 00
-WAIT 243c00
```

## Script `earith` slot 7

bytes 43 → 102

```diff
--- csr:D1:DEL1
+++ csr:D2:DEL1
@@ -1,5 +1,17 @@
+ANIME2 ae0401
+TURA ab0a0a02
+WINDOW 50020800080094003900
+MESSAGE 400210
+ANIME2 ae0401
+TURA ab070a02
 MOVA aa07
+REQSW 0207c9
+ANIME1 a30501
+WINDOW 50020800080019013900
+MESSAGE 400211
 MOVE a8009a007002
+WINDOW 50020800080097003900
+MESSAGE 400212
 REQSW 020ac8
 UC 3300
 MENU2 4a00
```

## Script `tifa` slot 7

bytes 40 → 60

```diff
--- csr:D1:DEL1
+++ csr:D2:DEL1
@@ -1,4 +1,8 @@
 SOLID c701
+ANIME2 ae0501
+TURA ab070a02
+WINDOW 50020800080028013900
+MESSAGE 40020f
 IFPRTYQ cb0320
 UC 3300
 MENU2 4a00
```

## Script `yufi` slot 31

bytes 47 → 60

```diff
--- csr:D1:DEL1
+++ csr:D2:DEL1
@@ -1,4 +1,6 @@
 SOLID c701
+WINDOW 50016400a000c9003900
+MESSAGE 400115
 MSPED b200000c
 MOVE a8008e03ec00
 DFANM a20401
```


## vs pristine (same disc)

- pristine D1 vs CSR D1: `scripts` (scripts_id=False, text_content=True, pad 446→2)
- pristine D2 vs CSR D2: `pad-only` (scripts_id=True, text_content=True, pad 446→2)
