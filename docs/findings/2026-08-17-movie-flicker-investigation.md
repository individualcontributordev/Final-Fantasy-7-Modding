# Finding: Movie Flicker Issues in Working v0.1.2

**Date:** 2026-08-17  
**Reporter:** User (individualcontributordev)  
**Status:** ⚠️ Investigating

## Reported Issues

User tested working v0.1.2 bin (`ff7-d1-csr-sd-mov-end.bin`) and reported:

1. **Ending movie:** Audio flickering
2. **Field 637 (LOSLAKE1), id 2, script 0, line 54:** Movie has flickering

## Field ID 637 = LOSLAKE1

From Makou Reactor field list (`makoureactor/src/Data.cpp`):
- Field ID 637 = **LOSLAKE1** (Lost Number lake area)

## Movie Analysis

### LOSLAKE1 Movies

Analyzed working v0.1.2 bin:
```
Entity 'cl' / Slot 31: 48 opcodes
  [Line 44] PMVIE f82f - Movie ID 0x2F (47)
```

**Only 1 PMVIE found in LOSLAKE1:**
- Movie ID: **0x2F (47)**
- Location: Entity 'cl', Slot 31, Line 44

**Note:** User mentioned "id 2, script 0, line 54" - need clarification on how to interpret this reference. The analysis found movie at entity 'cl'/Slot 31/Line 44.

### Movie 0x2F (47)

Need to identify what movie this is. FF7 movie list (from Makou Reactor):
- Movie files are in MOVIE/*.STR format
- Movie 0x2F needs cross-reference

## Ending Movie Issue

User reported the ending movie has audio flickering. Need to identify:
- Which field triggers ending sequence
- Which PMVIE call plays the ending
- Whether this is a disc 1/2/3 movie placement issue

## Hypothesis: Manip-Movies

User mentioned these are "manip-movies" (manipulation videos):
- These are FMVs that were originally on Disc 2 or Disc 3
- For single-disc, they need to be moved to Disc 1
- **Hypothesis:** The flickering is caused by incorrect movie data or pointers

## Next Steps

1. **Identify movie 0x2F:** What scene does this play?
2. **Find ending movie:** Which field/script triggers it?
3. **Check movie locations:** Are these movies properly injected from D2/D3?
4. **Compare with pristine:** Do these movies exist on pristine D1?
5. **Investigate PMVIE mechanics:** How are movies referenced (LBA, file path, index)?

## Tools Needed

- [ ] Create movie analyzer script
- [ ] Extract movie list from Makou Reactor
- [ ] Map PMVIE IDs to movie files
- [ ] Check ISO for movie file locations (MOVIE/*.STR)

## Related Files

- LOSLAKE1.DAT (field 637)
- MOVIE/ directory in ISO
- Movie index/pointer tables (need to find)

## Priority

**Low-Medium** - v0.1.2 is playable despite these issues. Can be fixed in v0.1.41 after v0.1.40 core functionality is complete.
