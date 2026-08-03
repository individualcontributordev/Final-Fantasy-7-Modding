# Task: No-swap — apply FIELD DSKCG+MOVIE stubs (manual test)

You run the patch tool + DuckStation. Agent reviews evidence. No pack ship yet.

## Goal

On a pristine D1 copy, stub engine ops:

1. Ask for disc never waits (DSKCG 0x0E)
2. Field Play movie never plays/hangs (MOVIE 0xF9)

No Makou Ask/Play deletes needed for those two. Supernova battle not fixed yet.

## Work image

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
mkdir -p workspace/iso-extract
cp -f workspace/pristine/FINALFANTASY7_D1.bin workspace/iso-extract/ff7_d1_noswap_work.bin
```

## Apply stubs

```bash
python3 mods/no-swap/scripts/stub_field_movie_dskcg.py \
  --disc-image workspace/iso-extract/ff7_d1_noswap_work.bin \
  --in-place
```

Optional: add --dry-run first. Expect DSKCG + MOVIE lines and write OK.

## Playtest (DuckStation)

1. Field FMV (intro or any) — skip, no hang
2. Disc-change hub if you have a save — no insert-disc wait
3. Supernova may still freeze (expected)

## Evidence

```
Tool output:
Work bin path:
Intro/FMV skip: PASS/FAIL/not tested
Disc Ask skip: PASS/FAIL/not tested
Compress/inject: OK/fail
Notes:
```

Say **check** when done. Commit INSTRUCTIONS only if you paste evidence in-repo.

## Out of scope

Builder pack; battle SNOVA stub; CSR whitelist.

cp -f workspace/pristine/FINALFANTASY7_D1.bin workspace/iso-extract/ff7_d1_noswap_work.bin
➜  Final-Fantasy-7-Modding git:(main) python3 mods/no-swap/scripts/stub_field_movie_dskcg.py \
  --disc-image workspace/iso-extract/ff7_d1_noswap_work.bin \
  --in-place
DSKCG @ 0x2523C: 0a80023c20d84290 -> 0800e00300000000
MOVIE @ 0x2CE94: 0a80023c20d84290 -> 0800e00300000000
recompressed FIELD.BIN 85435 -> 85358 (slot 85435)
wrote workspace\iso-extract\ff7_d1_noswap_work.bin

new game black screen, does not load first field