# Field compare: csr:D1:JUNAIR2 vs csr:D2:JUNAIR2

**Classification:** `scripts` (meaningful)

| | csr:D1:JUNAIR2 | csr:D2:JUNAIR2 | delta |
|--|--:|--:|--:|
| compressed | 16720 | 16720 | 0 |
| decompressed | 36448 | 36444 | -4 |
| script slots | 33 | 33 | |
| text entries | 165 | 165 | |
| text padding | 3 | 1 | -2 |

## Sections

- `scripts`: 21944 → 21940 (**DIFF**)
- `walkmesh`: 5556 → 5556 (same)
- `background`: 8008 → 8008 (same)
- `camera`: 40 → 40 (same)
- `inf`: 740 → 740 (same)
- `encounter`: 48 → 48 (same)
- `model_loader`: 84 → 84 (same)

Scripts identical: **False** (1 differing slots)
Text content identical: **True** (diff ids: [])
AKAO identical: **True**

## Script `dir` slot 0

bytes 160 → 158

```diff
--- csr:D1:JUNAIR2
+++ csr:D2:JUNAIR2
@@ -22,8 +22,7 @@
 MENU2 4a01
 WAIT 242800
 REQEW 0305c3
-IFSW 1620000090010046
-JMPF 103d
+IFSW 1620000090010044
 FADE 6b0000000000010400
 UC 3301
 MENU2 4a01
```


## vs pristine (same disc)

- pristine D1 vs CSR D1: `mixed` (scripts_id=False, text_content=False, pad 62→3)
- pristine D2 vs CSR D2: `mixed` (scripts_id=True, text_content=False, pad 62→1)
