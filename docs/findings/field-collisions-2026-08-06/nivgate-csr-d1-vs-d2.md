# Field compare: csr:D1:NIVGATE vs csr:D2:NIVGATE

**Classification:** `scripts` (meaningful)

| | csr:D1:NIVGATE | csr:D2:NIVGATE | delta |
|--|--:|--:|--:|
| compressed | 7378 | 7358 | -20 |
| decompressed | 13328 | 13292 | -36 |
| script slots | 141 | 141 | |
| text entries | 49 | 49 | |
| text padding | 2 | 3 | 1 |

## Sections

- `scripts`: 8344 → 8308 (**DIFF**)
- `walkmesh`: 664 → 664 (same)
- `background`: 3348 → 3348 (same)
- `camera`: 40 → 40 (same)
- `inf`: 740 → 740 (same)
- `encounter`: 48 → 48 (same)
- `model_loader`: 116 → 116 (same)

Scripts identical: **False** (18 differing slots)
Text content identical: **True** (diff ids: [])
AKAO identical: **True**

## Script `b_drct` slot 1

bytes 16 → 16

```diff
--- csr:D1:NIVGATE
+++ csr:D2:NIVGATE
@@ -1,2 +1,2 @@
-SPLIT 09000000d3fff7fb785200f7fb7820
+SPLIT 09000000d3fff7fb785200f7fb7808
 RET 00
```

## Script `b_drct` slot 31

bytes 16 → 16

```diff
--- csr:D1:NIVGATE
+++ csr:D2:NIVGATE
@@ -1,2 +1,2 @@
-SPLIT 090000005200f7fb78d3fff7fb7820
+SPLIT 090000005200f7fb78d3fff7fb7808
 RET 00
```

## Script `cefiros` slot 3

bytes 177 → 171

```diff
--- csr:D1:NIVGATE
+++ csr:D2:NIVGATE
@@ -1,5 +1,3 @@
-MSPED b2000008
-JMPF 10a5
 MOVE a800f7ff3ffb
 TURA ab061002
 ANIME1 a30801
```

## Script `cefiros` slot 6

bytes 13 → 17

```diff
--- csr:D1:NIVGATE
+++ csr:D2:NIVGATE
@@ -1,3 +1,4 @@
+MSPED b2000010
 MOVE a800f7ff3ffb
+RET 00
 TURNGEN b400f8022001
-RET 00
```

## Script `cefiros` slot 7

bytes 24 → 28

```diff
--- csr:D1:NIVGATE
+++ csr:D2:NIVGATE
@@ -1,6 +1,7 @@
-ANIME1 a30801
+MSPED b2000010
+MOVE a800f4ff41fc
+RET 00
 WINDOW 5001320014008b002900
 MESSAGE 400107
+ANIME1 a30801
 ANIMW ac
-MOVE a800f4ff41fc
-RET 00
```

## Script `cloud` slot 3

bytes 29 → 25

```diff
--- csr:D1:NIVGATE
+++ csr:D2:NIVGATE
@@ -1,7 +1,6 @@
 TLKON 7e00
 SOLID c700
 VISI a401
-MSPED b200000c
 MOVE a800baffe4f9
 MOVE a800e8ffd0fa
 UC 3300
```

## Script `cloud` slot 11

bytes 13 → 17

```diff
--- csr:D1:NIVGATE
+++ csr:D2:NIVGATE
@@ -1,3 +1,4 @@
+MSPED b200000c
 MOVE a800baffe4f9
 MOVE a8000b0084fb
 RET 00
```

## Script `cloud` slot 13

bytes 12 → 5

```diff
--- csr:D1:NIVGATE
+++ csr:D2:NIVGATE
@@ -1,5 +1,2 @@
 TURA ab0e0802
-ANIME1 a30801
-ANIMW ac
-WAIT 241e00
 RET 00
```

## Script `cloud` slot 17

bytes 21 → 5

```diff
--- csr:D1:NIVGATE
+++ csr:D2:NIVGATE
@@ -1,5 +1,2 @@
 TURA ab070f02
-ANIME1 a30901
-WINDOW 50013200140089002900
-MESSAGE 400125
 RET 00
```

## Script `hei1` slot 3

bytes 25 → 21

```diff
--- csr:D1:NIVGATE
+++ csr:D2:NIVGATE
@@ -1,4 +1,3 @@
-MSPED b200000c
 MOVE a8007e0040fb
 WAIT 241e00
 ANIME1 a30401
```

## Script `hei1` slot 31

bytes 21 → 25

```diff
--- csr:D1:NIVGATE
+++ csr:D2:NIVGATE
@@ -1,3 +1,4 @@
+MSPED b2000010
 MOVE a8007e0040fb
 WAIT 241e00
 ANIME1 a30401
```

## Script `hei2` slot 3

bytes 15 → 11

```diff
--- csr:D1:NIVGATE
+++ csr:D2:NIVGATE
@@ -1,4 +1,3 @@
-MSPED b200000c
 MOVE a80076ff85fb
 TURA ab060802
 RET 00
```

## Script `hei2` slot 31

bytes 11 → 15

```diff
--- csr:D1:NIVGATE
+++ csr:D2:NIVGATE
@@ -1,3 +1,4 @@
+MSPED b2000010
 MOVE a80076ff85fb
 TURA ab0e0802
 RET 00
```

## Script `line_jp` slot 2

bytes 118 → 116

```diff
--- csr:D1:NIVGATE
+++ csr:D2:NIVGATE
@@ -1,8 +1,7 @@
 UC 3301
 MENU2 4a01
-IFSW 1620000080010364
+IFSW 1620000080010362
 SETWORD 8120006101
-JMPF 1051
 FADE 6b0000000000080200
 FADEW 6c
 WINDOW 50016400960092002900
```

## Script `tifa` slot 1

bytes 61 → 84

```diff
--- csr:D1:NIVGATE
+++ csr:D2:NIVGATE
@@ -1,14 +1,17 @@
 UC 3301
 MENU2 4a01
 TURA ab060802
-ANIME1 a30301
 WINDOW 50010a000a009f003900
 MESSAGE 40012c
-WAIT 240a00
 SOUND f100c60040
 NFADE 2500000bffffff0100
 FADEW 6c
 WAIT 240a00
 SOUND f100c60040
+MAPJUMP 60250100000000000000
 MAPJUMP 60220100000000000000
 RET 00
+WINDOW 50010a000a009f003900
+MESSAGE 40012c
+WAIT 240a00
+ANIME1 a30301
```

## Script `tifa` slot 5

bytes 41 → 41

```diff
--- csr:D1:NIVGATE
+++ csr:D2:NIVGATE
@@ -1,8 +1,8 @@
+TURA ab0e0802
+RET 00
+CANM!2 bc05000901
+CANIM2 bb050a1d01
 WINDOW 50010a000a0096002900
 MESSAGE 40011c
-TURA ab0e0802
-CANM!2 bc05000901
 WINDOW 50010a000a0089002900
 MESSAGE 40011d
-CANIM2 bb050a1d01
-RET 00
```

## Script `tifa` slot 9

bytes 21 → 5

```diff
--- csr:D1:NIVGATE
+++ csr:D2:NIVGATE
@@ -1,5 +1,2 @@
 TURA ab0e0802
-ANIME1 a30601
-WINDOW 50010a000a0089002900
-MESSAGE 400124
 RET 00
```

## Script `zax` slot 5

bytes 13 → 17

```diff
--- csr:D1:NIVGATE
+++ csr:D2:NIVGATE
@@ -1,3 +1,4 @@
+MSPED b2000010
 MOVE a800baffe4f9
 MOVE a800e8ffd0fa
 RET 00
```


## vs pristine (same disc)

- pristine D1 vs CSR D1: `scripts` (scripts_id=False, text_content=True, pad 18→2)
- pristine D2 vs CSR D2: `scripts` (scripts_id=False, text_content=True, pad 18→3)
