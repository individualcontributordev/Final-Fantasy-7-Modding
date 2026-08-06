# Field compare: csr:D1:BUGIN1A vs csr:D2:BUGIN1A

**Classification:** `scripts` (meaningful)

| | csr:D1:BUGIN1A | csr:D2:BUGIN1A | delta |
|--|--:|--:|--:|
| compressed | 12117 | 12097 | -20 |
| decompressed | 26024 | 26020 | -4 |
| script slots | 126 | 126 | |
| text entries | 53 | 53 | |
| text padding | 1 | 3 | 2 |

## Sections

- `scripts`: 14296 → 14292 (**DIFF**)
- `walkmesh`: 1264 → 1264 (same)
- `background`: 9532 → 9532 (same)
- `camera`: 40 → 40 (same)
- `inf`: 740 → 740 (same)
- `encounter`: 48 → 48 (same)
- `model_loader`: 76 → 76 (same)

Scripts identical: **False** (3 differing slots)
Text content identical: **True** (diff ids: [])
AKAO identical: **True**

## Script `AD` slot 4

bytes 32 → 17

```diff
--- csr:D1:BUGIN1A
+++ csr:D2:BUGIN1A
@@ -1,6 +1,4 @@
-SETWORD 812000ed01
-MAPJUMP 601d02b4ff5e00260028
-RET 00
-MAPJUMP 601f0250fcabee300120
 SOUND f1002a0040
 MOVIE f9
+MAPJUMP 601f0250fcabee300120
+RET 00
```

## Script `AD` slot 7

bytes 270 → 285

```diff
--- csr:D1:BUGIN1A
+++ csr:D2:BUGIN1A
@@ -1,5 +1,6 @@
 SPLIT 09000000e1ff98ffa051009affa03c
 REQEW 030bc7
+JMPF 1064
 REQEW 0303c8
 REQEW 030bc8
 REQEW 0303c9
@@ -33,7 +34,9 @@
 REQ 0109c6
 REQ 0108c6
 REQ 010ac5
+WAIT 240500
 SETWORD 8120006f05
+MAPJUMP 601e02e3f8d5f8630020
 WAIT 245000
 IFUB 14d052010603
 JMPF 101b
```

## Script `BUGEN` slot 1

bytes 515 → 509

```diff
--- csr:D1:BUGIN1A
+++ csr:D2:BUGIN1A
@@ -8,12 +8,12 @@
 MESSAGE 400134
 UC 3300
 MENU2 4a00
-JMPFL 11d501
+JMPFL 11cf01
 IFSW 162000006d05040c
 SOLID c701
 REQEW 0303c7
 REQ 010cc7
-JMPFL 11c201
+JMPFL 11bc01
 IFSW 16200000f003047f
 PTURA 35000a02
 IFUB 143009020042
@@ -42,7 +42,7 @@
 MESSAGE 40010c
 UC 3300
 MENU2 4a00
-JMPFL 113c01
+JMPFL 113601
 IFSW 162000000b020437
 PTURA 35000802
 IFPRTYQ cb041a
@@ -51,14 +51,14 @@
 MESSAGE 400105
 UC 3300
 MENU2 4a00
-JMPFL 111601
+JMPFL 111001
 JMPF 1017
 ANIME2 ae0201
 WINDOW 50011e001e00d3003900
 MESSAGE 400104
 UC 3300
 MENU2 4a00
-JMPF 10fd
+JMPF 10f7
 IFUB 1430aa400652
 IFUB 1430a1200635
 IFUB 1430a1400618
@@ -79,9 +79,8 @@
 MESSAGE 400102
 UC 3300
 MENU2 4a00
-JMPF 10a6
+JMPF 10a0
 PTURA 35000802
-JMPFL 117700
 ANIME2 ae0201
 WINDOW 50011e001e0006014900
 MESSAGE 400101
@@ -107,7 +106,6 @@
 TURNGEN b400e0010301
 SCR2D 640000000000
 BITON 8230aa06
-JMPFL 110800
 WAIT 240a00
 REQEW 030cc3
 REQ 010cc4
```


## vs pristine (same disc)

- pristine D1 vs CSR D1: `scripts` (scripts_id=False, text_content=True, pad 2→1)
- pristine D2 vs CSR D2: `scripts` (scripts_id=False, text_content=True, pad 2→3)
