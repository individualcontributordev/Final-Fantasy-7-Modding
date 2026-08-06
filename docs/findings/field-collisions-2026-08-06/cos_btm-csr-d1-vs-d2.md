# Field compare: csr:D1:COS_BTM vs csr:D2:COS_BTM

**Classification:** `scripts` (meaningful)

| | csr:D1:COS_BTM | csr:D2:COS_BTM | delta |
|--|--:|--:|--:|
| compressed | 23141 | 23143 | 2 |
| decompressed | 41996 | 41996 | 0 |
| script slots | 192 | 192 | |
| text entries | 69 | 69 | |
| text padding | 3 | 3 | 0 |

## Sections

- `scripts`: 15548 → 15548 (**DIFF**)
- `walkmesh`: 10984 → 10984 (same)
- `background`: 14476 → 14476 (same)
- `camera`: 40 → 40 (same)
- `inf`: 740 → 740 (same)
- `encounter`: 48 → 48 (same)
- `model_loader`: 132 → 132 (same)

Scripts identical: **False** (3 differing slots)
Text content identical: **True** (diff ids: [])
AKAO identical: **True**

## Script `BUGEN` slot 3

bytes 43 → 43

```diff
--- csr:D1:COS_BTM
+++ csr:D2:COS_BTM
@@ -4,7 +4,7 @@
 TLKON 7e00
 SOLID c700
 VISI a401
-MSPED b200000c
+MSPED b2000004
 MOVE a800f0f914fa
 MOVE a80098f941f8
 DIR b30018
```

## Script `BUGEN` slot 31

bytes 30 → 30

```diff
--- csr:D1:COS_BTM
+++ csr:D2:COS_BTM
@@ -1,6 +1,6 @@
-RET 00
 WINDOW 500210001000b7003900
 MESSAGE 40023a
 WAIT 240500
 WINDOW 50011000960089002900
 MESSAGE 40013b
+RET 00
```

## Script `MES` slot 31

bytes 30 → 30

```diff
--- csr:D1:COS_BTM
+++ csr:D2:COS_BTM
@@ -1,6 +1,6 @@
-RET 00
 WINDOW 500064001000ca002900
 MESSAGE 400038
 WAIT 241400
 WINDOW 500114009600b1002900
 MESSAGE 400139
+RET 00
```


## vs pristine (same disc)

- pristine D1 vs CSR D1: `scripts` (scripts_id=False, text_content=True, pad 195→3)
- pristine D2 vs CSR D2: `scripts` (scripts_id=False, text_content=True, pad 195→3)
