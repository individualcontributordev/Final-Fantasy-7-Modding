# Field compare: csr:D1:RCKTIN7 vs csr:D2:RCKTIN7

**Classification:** `scripts` (meaningful)

| | csr:D1:RCKTIN7 | csr:D2:RCKTIN7 | delta |
|--|--:|--:|--:|
| compressed | 13186 | 13202 | 16 |
| decompressed | 24104 | 24136 | 32 |
| script slots | 55 | 55 | |
| text entries | 213 | 213 | |
| text padding | 1 | 2 | 1 |

## Sections

- `scripts`: 15188 → 15220 (**DIFF**)
- `walkmesh`: 756 → 756 (same)
- `background`: 7228 → 7228 (same)
- `camera`: 40 → 40 (same)
- `inf`: 740 → 740 (same)
- `encounter`: 48 → 48 (same)
- `model_loader`: 76 → 76 (same)

Scripts identical: **False** (1 differing slots)
Text content identical: **True** (diff ids: [])
AKAO identical: **True**

## Script `init` slot 0

bytes 39 → 70

```diff
--- csr:D1:RCKTIN7
+++ csr:D2:RCKTIN7
@@ -1,6 +1,10 @@
 MPNAM 4305
 RET 00
 FADE 6b0000000000010400
+MMBUK cf08
+SETWORD 8120002605
+AKAO f2000000c1400000000000000000
+MAPJUMP 60480000000000000000
 IFUB 14300a080006
 PREQ 0402c3
 JMPF 1004
```


## vs pristine (same disc)

- pristine D1 vs CSR D1: `pad-only` (scripts_id=True, text_content=True, pad 37→1)
- pristine D2 vs CSR D2: `scripts` (scripts_id=False, text_content=True, pad 37→2)
