# BLACKBGB Pristine Has No MAPJUMP

**Date:** 2026-08-16  
**Context:** Investigating disc 1→2 transition for single-disc mod  
**Method:** Direct analysis of pristine FIELD/BLACKBGB.DAT from D1 and D2

## Finding

Analyzed pristine (unmodded) BLACKBGB.DAT from both discs:

| Disc | MAPJUMP opcodes | MUSIC opcodes | Note |
|------|-----------------|---------------|------|
| D1 | **0** | 5 (in cloud/script31) | MUSIC ids: 32, 128, 16, 64, 0 |
| D2 | **0** | 5 (in cloud/script31) | Identical to D1 |

**Both discs have the exact same BLACKBGB.DAT** - no MAPJUMP opcodes at all.

## Implication

The `MAPJUMP #634` we've been seeing in single-disc findings is **added by CSR**, not from the vanilla game.

On pristine multi-disc:
- BLACKBGB is a simple "disc swap hub" 
- Shows a message (via mes1/mes2/mes3 entities)
- The game's kernel/CD code handles the actual disc transition
- No field-level MAPJUMP needed because the kernel detects the new disc

## For Single-Disc Mod

Since there's no disc swap on single-disc, we need to:
1. Find out what CSR does to BLACKBGB 
2. Determine if CSR adds the MAPJUMP or if it comes from single-disc
3. Ensure the MAPJUMP goes to the right field (#526 for break scene, or #634 for forest)

## Method Used

```python
from field_dat import load_field_dat
from psx_mode2_iso import extract_file
from lzs import decompress_all_with_header

img = Path("workspace/pristine/FINALFANTASY7_D1.bin").read_bytes()
compressed = extract_file(img, "FIELD/BLACKBGB.DAT")
field_data = decompress_all_with_header(compressed)
dat = load_field_dat(field_data)

# Parse all scripts looking for MAPJUMP (0x2B) and MUSIC (0x31)
for script in dat.scripts:
    # ... parse opcodes
```

## Next

Test CSR multi-disc to see:
1. What CSR adds to BLACKBGB (if anything)
2. What the actual disc 1→2 flow is
3. Where the break scene happens and how it's triggered
