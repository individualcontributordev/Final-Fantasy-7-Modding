# Status: ending credits v6 verified

DuckStation: post-final-battle ending path works with v6  
(D3 absolute LBAs for ENDING* / LASTFLOR / LASTMAP.BIN).

## What fixed it

Ending FMV seeks **Disc 3 file LBAs** (e.g. ENDING01 @ **163608**), not only  
a rewritten `MOVIE_ID` row at a grown end-of-image address.

- Tool: `mods/single-disc/scripts/alias_d3_ending_lbas_on_d1.py`  
- Builder: `mods/single-disc/scripts/build_ending_credits_test_bin.py`  
- Finding: `docs/findings/2026-08-07-ending-credits-test-inject.md`  
- Test cue: `workspace/iso-extract/ff7_d1_playtest_ending_test.cue`  

Still oversize-test / not in builder packs; still overwrites D1 movie ranges  
at those LBAs. Next product work is reclaim-for-CD or ship path if you want that.

## Rebuild (optional)

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only
python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
```
