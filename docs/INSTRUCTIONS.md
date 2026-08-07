# Status: ending credits disc image — playtest pass

## Result

User tested `ff7_d1_playtest_ending_test` (built with the ending-credits script after the manip stack).

**All worked fine** — lake cutscene and ending/credits path.

Note on file: `docs/findings/2026-08-07-ending-credits-cd-playtest-pass.md`

## What that image is

1. Speedrun base + single-disc + manip movies  
2. Ending/credits movies written onto the disc where the game looks for them  
3. Lake movie put back on its fixed disc spot  
4. Small speedrun movies put back if the long credits had covered them  
5. Map scripts left as the mod already had them (skipped movies stay skipped on purpose)

## Rebuild (if needed)

```bash
python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
# workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

## Possible next (no step assigned yet)

- Fold this ending step into the normal single-disc ship/build so a release disc includes credits without a separate test script  
- Or leave the test script as the way to make a credits burn until you ask to ship it  
