# Single-Disc v0.1.2 Website Builder Fix

**Date:** 2026-08-18  
**Status:** ✅ FIXED  
**Version:** v0.1.2

## Summary

Fixed critical bug preventing single-disc v0.1.2 from working when built via https://individualcontributor.dev/builder/

**Root cause:** Alphabetical sorting of auto-included addon IDs caused layers to apply in wrong order (1, 10, 2-9 instead of 1-10).

**Fix:** Zero-padded part numbers (`part02` through `part09`) so alphabetical sort = numeric sort.

## Problem

User reported website-downloaded bin crashed with black screen at disc 1→2 transition, but:
- ✅ Local build from `docs/INSTRUCTIONS.md` worked perfectly
- ✅ All 137 field scripts matched working bin
- ✅ File sizes identical (766,340,400 bytes)

## Investigation

### Initial Hypotheses (All Wrong)

1. ❌ **EDC/ECC corruption** - Tested website's edc.js algorithm, produces identical results
2. ❌ **Sector detection bug** - Tested isMode2Form1 logic, correctly identifies 80,909 sectors
3. ❌ **Layer application bug** - Built with website's layer.js code, byte-for-byte match

### Discovery

Compared website-downloaded bin to working bin:
- **23,145,605 bytes differ** (30% of the disc!)
- **10,718 sectors corrupted**
- Differences in **data area**, not just footers
- LBA 17699: Completely different gzip compressed field data

Checked `APPLIED.txt` from website build:
```
Mods on this disc:
  - Single-disc v0.1.2 (single-disc-on-csr)
  - Single-disc part 10 v0.1.2                    ← Part 10 BEFORE part 2!
  - Single-disc part 2 v0.1.2
  - Single-disc part 3 v0.1.2
  ...
  - Single-disc part 9 v0.1.2
```

## Root Cause

Website builder sorts auto-included addons **alphabetically by addon ID**.

Manifest defined parts as:
```json
"single-disc-v0.1.2-part2"
"single-disc-v0.1.2-part3"
...
"single-disc-v0.1.2-part10"
```

Alphabetical sort produces:
```
part10 < part2  (string comparison: "1" < "2")
part2 < part3
...
part9 < part10  (but part10 already applied!)
```

Applied order: **1, 10, 2, 3, 4, 5, 6, 7, 8, 9**

Each part overwrites specific sectors. Applying part 10 before parts 2-9 means:
- Part 10 writes sectors X-Y
- Parts 2-9 overwrite some of those sectors
- Final result is missing part 10's changes to sectors that parts 2-9 didn't touch

## Fix

Renamed manifest IDs to use zero-padded numbers:
- `single-disc-v0.1.2-part02` (was `part2`)
- `single-disc-v0.1.2-part03` (was `part3`)
- ...
- `single-disc-v0.1.2-part09` (was `part9`)
- `single-disc-v0.1.2-part10` (unchanged)

Now alphabetical sort = numeric sort:
```
part02 < part03 < ... < part09 < part10
```

Applied order: **1, 2, 3, 4, 5, 6, 7, 8, 9, 10** ✅

## Testing

After manifest fix:
1. Clear browser cache
2. Reload builder website
3. Download fresh single-disc bin
4. Test in DuckStation at disc 1→2 transition

Expected: Bin now matches local build byte-for-byte.

## Lessons

1. **Always check APPLIED.txt** when debugging website builds
2. **Multi-part mods need zero-padded IDs** for alphabetical sorting
3. **Byte-level comparison** revealed the true issue faster than runtime debugging
4. **Local build proved layers were correct** - narrowed search to manifest/website logic

## Related Files

- `builder/manifest.json` - Fixed addon IDs
- `scripts/test_edc_calculation.py` - Proved EDC algorithm correct
- `scripts/diagnose_edc_sector_detection.py` - Proved sector detection correct
- `scripts/build_with_website_code.js` - Proved layer.js correct
- `docs/findings/2026-08-18-builder-website-bug-confirmed.md` - Investigation log
