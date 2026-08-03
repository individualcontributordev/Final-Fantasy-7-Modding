# Task: No-swap — retest FIELD stubs v2 (PC advance)

Prior v1 bare jr-ra caused **new game black screen** (MOVIE never advanced script PC).

v2 stubs: complete opcode by script PC += size, then return (no FMV / no disc wait).

## Apply (fresh pristine recommended)

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
cp -f workspace/pristine/FINALFANTASY7_D1.bin workspace/iso-extract/ff7_d1_noswap_work.bin
python3 mods/no-swap/scripts/stub_field_movie_dskcg.py \
  --disc-image workspace/iso-extract/ff7_d1_noswap_work.bin \
  --in-place
```

Expect DSKCG PC+2 and MOVIE PC+1, recompress OK.

## Playtest

1. **New game** — must leave black screen and reach Midgar field (or continue past first MOVIE)
2. Field FMV — skip, no hang
3. Disc-change hub if available — no insert wait
4. Supernova — may still freeze (not patched)

## Evidence

```
Tool output:
New game / first field: PASS/FAIL
FMV skip: PASS/FAIL/not tested
Disc Ask: PASS/FAIL/not tested
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