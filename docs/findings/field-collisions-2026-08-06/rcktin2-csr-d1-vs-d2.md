# Field compare: csr:D1:RCKTIN2 vs csr:D2:RCKTIN2

**Classification:** `scripts` (meaningful)

| | csr:D1:RCKTIN2 | csr:D2:RCKTIN2 | delta |
|--|--:|--:|--:|
| compressed | 17713 | 17709 | -4 |
| decompressed | 35656 | 35656 | 0 |
| script slots | 67 | 67 | |
| text entries | 213 | 213 | |
| text padding | 0 | 1 | 1 |

## Sections

- `scripts`: 27096 → 27096 (**DIFF**)
- `walkmesh`: 1236 → 1236 (same)
- `background`: 6392 → 6392 (same)
- `camera`: 40 → 40 (same)
- `inf`: 740 → 740 (same)
- `encounter`: 48 → 48 (same)
- `model_loader`: 76 → 76 (same)

Scripts identical: **False** (2 differing slots)
Text content identical: **True** (diff ids: [])
AKAO identical: **True**

## Script `cid` slot 1

bytes 656 → 653

```diff
--- csr:D1:RCKTIN2
+++ csr:D2:RCKTIN2
@@ -1,6 +1,6 @@
 IFUB 14500a030004
 RET 00
-JMPF 10e1
+JMPF 10f4
 IFUB 14500d01000f
 WINDOW 500208009100bf003900
 MESSAGE 40021c
@@ -11,7 +11,7 @@
 WCLSE 5402
 WAIT 240800
 PTURA 35001002
-IFUB 143082020a38
+IFUB 143082020a4b
 REQ 0101c3
 WINDOW 500208009100c8001900
 MESSAGE 400207
@@ -25,6 +25,10 @@
 CANM!2 bc070d2701
 IFUB 145011000003
 JMPB 120b
+ANIME2 ae0801
+WINDOW 500208009100ff003900
+MESSAGE 40020a
+WAIT 240400
 SETBYTE 80500b02
 ANIME2 ae0901
 WINDOW 500208008200fd005900
@@ -75,7 +79,6 @@
 CANM!2 bc070d2701
 IFUB 145011000003
 JMPB 120b
-JMPFL 112e01
 ANIME1 a30801
 WINDOW 50020800910099003900
 MESSAGE 40020d
@@ -153,8 +156,4 @@
 WINDOW 500208009100bf003900
 MESSAGE 40021c
 INC 95050d
-JMPBL 139a01
-ANIME2 ae0801
-WINDOW 500208009100ff003900
-MESSAGE 40020a
-WAIT 240400
+JMPBL 139701
```

## Script `leader` slot 0

bytes 184 → 186

```diff
--- csr:D1:RCKTIN2
+++ csr:D2:RCKTIN2
@@ -18,9 +18,9 @@
 VISI a400
 RET 00
 SLIDR c6000f
-IFUB 143085010972
-IFUB 14308502096c
-IFUB 143085030a61
+IFUB 143085010974
+IFUB 14308502096e
+IFUB 143085030a63
 UC 3301
 MENU2 4a01
 BITON 82308503
@@ -30,6 +30,7 @@
 ANIME2 ae0301
 WINDOW 5003200008000e013900
 MESSAGE 400349
+JMPF 1017
 REQEW 0306c8
 WAIT 240400
 ANIM!1 af0401
```


## vs pristine (same disc)

- pristine D1 vs CSR D1: `scripts` (scripts_id=False, text_content=True, pad 35→0)
- pristine D2 vs CSR D2: `scripts` (scripts_id=False, text_content=True, pad 35→1)
