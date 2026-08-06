# Field compare: csr:D1:LOST2 vs csr:D2:LOST2

**Classification:** `scripts` (meaningful)

| | csr:D1:LOST2 | csr:D2:LOST2 | delta |
|--|--:|--:|--:|
| compressed | 17007 | 17090 | 83 |
| decompressed | 32132 | 32304 | 172 |
| script slots | 69 | 71 | |
| text entries | 148 | 148 | |
| text padding | 2 | 2 | 0 |

## Sections

- `scripts`: 14192 → 14364 (**DIFF**)
- `walkmesh`: 3996 → 3996 (same)
- `background`: 13012 → 13012 (same)
- `camera`: 40 → 40 (same)
- `inf`: 740 → 740 (same)
- `encounter`: 48 → 48 (same)
- `model_loader`: 76 → 76 (same)

Scripts identical: **False** (22 differing slots)
Text content identical: **True** (diff ids: [])
AKAO identical: **True**

Entities A: ['init', 'fade', 'Info', 'line', 'jump', 'cloud', 'ballet', 'tifa', 'red13', 'cid', 'yufi', 'ketcy', 'vincent', 'cefir']
Entities B: ['version', 'init', 'fade', 'Info', 'line', 'jump', 'cloud', 'ballet', 'tifa', 'red13', 'cid', 'yufi', 'ketcy', 'vincent', 'cefir']

## Script `Info` slot 4

bytes 17 → 17

```diff
--- csr:D1:LOST2
+++ csr:D2:LOST2
@@ -2,4 +2,4 @@
 UC 3301
 MENU2 4a01
 BITOFF 83308901
-REQEW 0305c7
+REQEW 0306c7
```

## Script `ballet` slot 3

bytes 98 → 98

```diff
--- csr:D1:LOST2
+++ csr:D2:LOST2
@@ -1,4 +1,4 @@
-AXYZI c166660500020406
+AXYZI c166660600020406
 XYZI a566660000020004000600
 DIR b30060
 TLKON 7e00
@@ -11,13 +11,13 @@
 MESSAGE 40014e
 IFUB 145008000003
 JMPB 1206
-REQEW 0305c5
+REQEW 0306c5
 ANIMW ac
 WAIT 240400
 ANIME2 ae0401
 WINDOW 50011c00080016014900
 MESSAGE 40017b
-REQ 0105c6
+REQ 0106c6
 IFUB 145008010003
 JMPB 1206
 TLKON 7e01
```

## Script `ballet` slot 5

bytes 5 → 5

```diff
--- csr:D1:LOST2
+++ csr:D2:LOST2
@@ -1,2 +1,2 @@
-TURA ab050102
+TURA ab060102
 RET 00
```

## Script `cefir` slot 31

bytes 256 → 258

```diff
--- csr:D1:LOST2
+++ csr:D2:LOST2
@@ -1,3 +1,4 @@
+JMPF 10fd
 TLKON 7e00
 SOLID c700
 VISI a401
@@ -86,5 +87,5 @@
 VISI a400
 PRQEW 0601c5
 PRQEW 0602c5
-REQ 0105c8
+REQ 0106c8
 RET 00
```

## Script `cid` slot 3

bytes 98 → 98

```diff
--- csr:D1:LOST2
+++ csr:D2:LOST2
@@ -1,4 +1,4 @@
-AXYZI c166660500020406
+AXYZI c166660600020406
 XYZI a566660000020004000600
 DIR b30060
 TLKON 7e00
@@ -11,13 +11,13 @@
 MESSAGE 400154
 IFUB 145008000003
 JMPB 1206
-REQEW 0305c5
+REQEW 0306c5
 ANIMW ac
 WAIT 240400
 ANIME2 ae0401
 WINDOW 50011c00080002014900
 MESSAGE 40017e
-REQ 0105c6
+REQ 0106c6
 IFUB 145008010003
 JMPB 1206
 TLKON 7e01
```

## Script `cid` slot 5

bytes 5 → 5

```diff
--- csr:D1:LOST2
+++ csr:D2:LOST2
@@ -1,2 +1,2 @@
-TURA ab050102
+TURA ab060102
 RET 00
```

## Script `cloud` slot 7

bytes 258 → 260

```diff
--- csr:D1:LOST2
+++ csr:D2:LOST2
@@ -1,5 +1,6 @@
 MOVE a800b6fa0b12
 SPLIT 090000000efaed116062fa6d128010
+JMPF 10de
 PREQ 0402c4
 IFUB 14300b010010
 WINDOW 500208002300bc003900
@@ -37,7 +38,7 @@
 WINDOW 50008c00320089002900
 MESSAGE 400091
 SCR2DL 6800000a001e002000
-REQ 010dc3
+REQ 010ec3
+RET 00
+NFADE 2500000c0801402000
 WAIT 240300
-NFADE 2500000c0801402000
-RET 00
```

## Script `cloud` slot 31

bytes 92 → 109

```diff
--- csr:D1:LOST2
+++ csr:D2:LOST2
@@ -1,3 +1,4 @@
+JMPF 1058
 DFANM a20601
 WAIT 242800
 PRQEW 0601c6
@@ -14,6 +15,9 @@
 AKAO f2000000a07f0000000000000000
 NFADE 250000000000000000
 SCRCC 65
+WINDOW 50006e002800c2004900
+MESSAGE 400090
+JOIN 0810
 UC 3300
 MENU2 4a00
 RET 00
```

## Script `init` slot 0

bytes 209 → 268

```diff
--- csr:D1:LOST2
+++ csr:D2:LOST2
@@ -1,13 +1,19 @@
 MPNAM 4300
-IFUB 14308404090d
-IFUW 1820000055a40105
+IFUB 14308404091c
+IFUW 1820000055a40112
+AKAO2 da0000009a00000000000000000000
 MUSIC f000
-JMPF 100b
-IFUW 1820000055a40103
+JMPF 101a
+IFUW 1820000055a40112
+AKAO2 da0000009a00000000000000000000
 MUSIC f001
 RET 00
+IFUW 1820000055a4000b
+MAPJUMP 600e027bff1cfa6500e0
+IFSW 16200000a5020004
+REQ 0100c1
 IFUB 143084040904
-REQ 0101c3
+REQ 0102c3
 AKAO f200000028400000000000000000
 AKAO f200000029400000000000000000
 AKAO f20000002a400000000000000000
```

## Script `ketcy` slot 3

bytes 98 → 98

```diff
--- csr:D1:LOST2
+++ csr:D2:LOST2
@@ -1,4 +1,4 @@
-AXYZI c166660500020406
+AXYZI c166660600020406
 XYZI a566660000020004000600
 DIR b30060
 TLKON 7e00
@@ -11,13 +11,13 @@
 MESSAGE 400158
 IFUB 145008000003
 JMPB 1206
-REQEW 0305c5
+REQEW 0306c5
 ANIMW ac
 WAIT 240400
 ANIME2 ae0401
 WINDOW 50011c00080022013900
 MESSAGE 400180
-REQ 0105c6
+REQ 0106c6
 IFUB 145008010003
 JMPB 1206
 TLKON 7e01
```

## Script `ketcy` slot 5

bytes 5 → 5

```diff
--- csr:D1:LOST2
+++ csr:D2:LOST2
@@ -1,2 +1,2 @@
-TURA ab050102
+TURA ab060102
 RET 00
```

## Script `line` slot 3

bytes 36 → 36

```diff
--- csr:D1:LOST2
+++ csr:D2:LOST2
@@ -1,10 +1,10 @@
 IFUB 143084040906
-REQEW 0305c3
+REQEW 0306c3
 JMPF 1019
 IFSW 1620000098020311
 IFUB 143084040a0b
 UC 3301
 MENU2 4a01
 PREQ 0402c3
-REQ 0105c4
+REQ 0106c4
 RET 00
```

## Script `red13` slot 3

bytes 98 → 98

```diff
--- csr:D1:LOST2
+++ csr:D2:LOST2
@@ -1,4 +1,4 @@
-AXYZI c166660500020406
+AXYZI c166660600020406
 XYZI a566660000020004000600
 DIR b30060
 TLKON 7e00
@@ -11,13 +11,13 @@
 MESSAGE 400152
 IFUB 145008000003
 JMPB 1206
-REQEW 0305c5
+REQEW 0306c5
 ANIMW ac
 WAIT 240400
 ANIME2 ae0401
 WINDOW 50011c00080018014900
 MESSAGE 40017d
-REQ 0105c6
+REQ 0106c6
 IFUB 145008010003
 JMPB 1206
 TLKON 7e01
```

## Script `red13` slot 5

bytes 5 → 5

```diff
--- csr:D1:LOST2
+++ csr:D2:LOST2
@@ -1,2 +1,2 @@
-TURA ab050102
+TURA ab060102
 RET 00
```

## Script `tifa` slot 3

bytes 98 → 98

```diff
--- csr:D1:LOST2
+++ csr:D2:LOST2
@@ -1,4 +1,4 @@
-AXYZI c166660500020406
+AXYZI c166660600020406
 XYZI a566660000020004000600
 DIR b30060
 TLKON 7e00
@@ -11,13 +11,13 @@
 MESSAGE 400150
 IFUB 145008000003
 JMPB 1206
-REQEW 0305c5
+REQEW 0306c5
 ANIMW ac
 WAIT 240400
 ANIME2 ae0401
 WINDOW 50011c00080028014900
 MESSAGE 40017c
-REQ 0105c6
+REQ 0106c6
 IFUB 145008010003
 JMPB 1206
 TLKON 7e01
```

## Script `tifa` slot 5

bytes 5 → 5

```diff
--- csr:D1:LOST2
+++ csr:D2:LOST2
@@ -1,2 +1,2 @@
-TURA ab050102
+TURA ab060102
 RET 00
```

## Script `version` slot 0

bytes 0 → 2

```diff
--- csr:D1:LOST2
+++ csr:D2:LOST2
@@ -0,0 +1,2 @@
+RET 00
+RET 00
```

## Script `version` slot 31

bytes 0 → 18

```diff
--- csr:D1:LOST2
+++ csr:D2:LOST2
@@ -0,0 +1,4 @@
+RET 00
+WMODE 52030101
+WINDOW 50030800c60067001900
+MESSAGE 400393
```

## Script `vincent` slot 3

bytes 98 → 98

```diff
--- csr:D1:LOST2
+++ csr:D2:LOST2
@@ -1,4 +1,4 @@
-AXYZI c166660500020406
+AXYZI c166660600020406
 XYZI a566660000020004000600
 DIR b30060
 TLKON 7e00
@@ -11,13 +11,13 @@
 MESSAGE 40015a
 IFUB 145008000003
 JMPB 1206
-REQEW 0305c5
+REQEW 0306c5
 ANIMW ac
 WAIT 240400
 ANIME2 ae0401
 WINDOW 50011c0008002a014900
 MESSAGE 400181
-REQ 0105c6
+REQ 0106c6
 IFUB 145008010003
 JMPB 1206
 TLKON 7e01
```

## Script `vincent` slot 5

bytes 5 → 5

```diff
--- csr:D1:LOST2
+++ csr:D2:LOST2
@@ -1,2 +1,2 @@
-TURA ab050102
+TURA ab060102
 RET 00
```

_… 2 more script slots omitted_

## vs pristine (same disc)

- pristine D1 vs CSR D1: `mixed` (scripts_id=False, text_content=False, pad 2→2)
- pristine D2 vs CSR D2: `mixed` (scripts_id=False, text_content=False, pad 2→2)
