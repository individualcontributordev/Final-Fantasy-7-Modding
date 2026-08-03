# Task: No-swap — test v6 DSKCG force-complete

## Last results

- v5 DSKCG-only: **intro + first field PASS** (MOVIE vanilla good)
- Disc-change: **no Ask UI**, but **black + silence** (stuck on blackbgb / never
  music+MAPJUMP after DSKCG)

blackbgb is a black map; after a working DSKCG the script should still hit
**Play music** then **Jump** to lost2/las0_1. No sound ⇒ script not past DSKCG.

## v6 change

DSKCG force-complete with:
- stack + ra save
- entity* null check; if set, clear wait byte@1
- script PC += 2
- return 0  
MOVIE still vanilla.

## Apply

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
cp -f workspace/pristine/FINALFANTASY7_D1.bin workspace/iso-extract/ff7_d1_noswap_work.bin
python3 mods/no-swap/scripts/stub_field_movie_dskcg.py \
  --disc-image workspace/iso-extract/ff7_d1_noswap_work.bin \
  --in-place
```

Expect: `DSKCG ... v6 force-complete` and `MOVIE: left vanilla`.

## Playtest

1. New game still OK (intro + field)
2. Disc-change hub save:
   - no insert-disc UI
   - **music after** and/or **map jump** to lost2 / las0_1 (not permanent black silence)

## Evidence

```
Tool (v6):
New game still OK: PASS/FAIL
Disc-change: PASS/FAIL
  - music after? 
  - jumped to lost2/las0_1?
Notes:
```

Say **check**.

## Fallback if v6 still black+silent

Switch to **Makou-only** Ask removal on all DSKCG maps (proven on blackbgb earlier)
plus vanilla FIELD; engine FMV skip later via another hook.
