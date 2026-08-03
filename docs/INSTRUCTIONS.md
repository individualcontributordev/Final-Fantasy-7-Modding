# Task: No-swap — retest FIELD stubs v3 (full completion)

## What failed

- v1 jr-ra: black screen (no script PC advance)
- v2 PC+ only: you heard movie audio, then still no first field — MOVIE is a
  multi-frame state machine; finishing needs entity state/flag clears too

## v3

MOVIE stub now:
- clear entity byte@1 and half@38 (movie wait state)
- script PC += 1
- clear 0x80071C1C and 0x801144D4 (flags original path touches)
- return 0

DSKCG: clear entity state + PC += 2 + return 0

## Apply

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
cp -f workspace/pristine/FINALFANTASY7_D1.bin workspace/iso-extract/ff7_d1_noswap_work.bin
python3 mods/no-swap/scripts/stub_field_movie_dskcg.py \
  --disc-image workspace/iso-extract/ff7_d1_noswap_work.bin \
  --in-place
```

## Playtest (critical)

1. **New game** — must reach Midgar / first field after intro (no permanent black)
2. Intro FMV — ideally skipped or silent skip; must not softlock after audio
3. Note if you still hear full intro audio with black video (partial)

Optional: disc-change hub if you have a save.

## Evidence

```
Tool output:
New game reaches field: PASS/FAIL
Intro behavior:
Notes:
```

Say **check**.

  Final-Fantasy-7-Modding git:(main) cp -f workspace/pristine/FINALFANTASY7_D1.bin workspace/iso-extract/ff7_d1_noswap_work.bin
python3 mods/no-swap/scripts/stub_field_movie_dskcg.py \
  --disc-image workspace/iso-extract/ff7_d1_noswap_work.bin \
  --in-place
DSKCG @ 0x2523C: 64 bytes (PC+2)
  was 0a80023c20d84290e8ffbd2703004230...
  now e8ffbd271000bfaf0780083cc4220891...
MOVIE @ 0x2CE94: 64 bytes (PC+1)
  was 0a80023c20d84290e8ffbd2703004230...
  now e8ffbd271000bfaf0780083cc4220891...
recompressed FIELD.BIN 85435 -> 85368 (slot 85435)
wrote workspace\iso-extract\ff7_d1_noswap_work.bin