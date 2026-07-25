# field_map_init — Danger=0 hook (fe8c steal rejected)

**Date:** 2026-07-25  
**Confidence:** confirmed (reject)  
**Related:** [dat-8009fe8c-xrefs](2026-07-25-dat-8009fe8c-xrefs.md), [field-map-setup](2026-07-25-field-map-setup.md)

## Summary

Cannot replace `DAT_8009fe8c = 0` @ `0x800BA574`–`0x800BA578` with `g_danger = 0` — flag has ~28 reads.

## Next hook candidates

1. **Map-setup block** `LAB_800a1dc8` (`0x800A1DC8`) — already many `sh zero`; retarget or find spare pair
2. Steal a lighter clear (e.g. `DAT_80095dcc`) after xref check
3. Trampoline/cave if no 2-ins slot

## Follow-ups

- [ ] Paste Listing `0x800A1DC8` → `jal field_map_init`
- [ ] Pick exact 2-ins Danger=0 patch
