# Field compare: csr:D1:BLACKBGB vs csr:D2:BLACKBGB

**Classification:** `scripts` (meaningful)

| | csr:D1:BLACKBGB | csr:D2:BLACKBGB | delta |
|--|--:|--:|--:|
| compressed | 13013 | 13013 | 0 |
| decompressed | 23908 | 23908 | 0 |
| script slots | 30 | 30 | |
| text entries | 38 | 38 | |
| text padding | 2 | 2 | 0 |

## Sections

- `scripts`: 13964 → 13964 (**DIFF**)
- `walkmesh`: 604 → 604 (same)
- `background`: 8440 → 8440 (same)
- `camera`: 56 → 56 (same)
- `inf`: 740 → 740 (same)
- `encounter`: 48 → 48 (same)
- `model_loader`: 28 → 28 (same)

Scripts identical: **False** (1 differing slots)
Text content identical: **True** (diff ids: [])
AKAO identical: **True**

## Script `init` slot 0

bytes 802 → 802

```diff
--- csr:D1:BLACKBGB
+++ csr:D2:BLACKBGB
@@ -20,11 +20,11 @@
 BITOFF 83308807
 MENU 49031500
 BATTLE 7000d401
-MAPJUMP 60e20025fbdeff320000
 AKAO f2000000c1ff0000000000000000
 WAIT 245000
 MUSIC f000
 AKAO f2000000c1007f00000000000000
+MAPJUMP 60e20025fbdeff320000
 IFUB 14d05b020930
 BITON 82308807
 BITOFF 83d05b02
```


## vs pristine (same disc)

- pristine D1 vs CSR D1: `mixed` (scripts_id=False, text_content=False, pad 3→2)
- pristine D2 vs CSR D2: `mixed` (scripts_id=False, text_content=False, pad 3→2)
