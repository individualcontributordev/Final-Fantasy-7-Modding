# Your turn: build and test the credits disc image

## Goal

Put the ending / credits movies on the single-disc image and try them in DuckStation.  
Lake movie stays working. Long credits may still show broken name text in the middle (known tradeoff).

Map scripts stay as after the speedrun + single-disc stack (no “restore vanilla maps” step).

## Build

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only
python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
```

Open:

```text
workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

## What to check

1. **Lake cutscene** — still plays with picture and sound.  
2. **After the final battle** — ending / credits movies run enough to finish.  
3. **Rolling names** — fine if some names look like noise for a while; the scroll can still be OK. Say if the run hard-stops or never starts.

## Reply with

- Lake: OK / fail  
- Credits: OK / fail / OK but messy names  
- Anything that hard-crashed or softlocked  

Push logs into the repo only if you want them reviewed on **check**.
