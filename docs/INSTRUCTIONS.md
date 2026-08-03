# Task: No-swap — test v5 DSKCG-only (MOVIE vanilla)

## Status of MOVIE stubs

| Ver | Result |
|-----|--------|
| v1–v4 MOVIE entry stubs | FAIL — black screen, intro audio, field never loads |

**Stop replacing the MOVIE opcode for now.** Intro/FMV on D1 needs the real handler.

## v5 strategy

1. **DSKCG only** — skip disc-change wait (PC+2, no entity writes)
2. **MOVIE left pristine** — new game / field FMV should work on D1
3. Missing FMV / Supernova later via a different hook (stream layer), not 0xF9 entry

## Apply

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
cp -f workspace/pristine/FINALFANTASY7_D1.bin workspace/iso-extract/ff7_d1_noswap_work.bin
python3 mods/no-swap/scripts/stub_field_movie_dskcg.py \
  --disc-image workspace/iso-extract/ff7_d1_noswap_work.bin \
  --in-place
```

Expect:
- `DSKCG @ ... v5`
- `MOVIE: left vanilla`

Do **not** pass `--also-movie` unless experimenting.

## Playtest

1. **New game** — must show intro **video** (not black) and reach first field
2. Optional: disc-change hub save — no insert-disc lock
3. Do not expect FMV-cut yet

## Evidence

```
Tool output:
New game intro video + first field: PASS/FAIL
Disc Ask (if tested): PASS/FAIL/not tested
Notes:
```

Say **check**.

## If new game still fails on DSKCG-only

Then FIELD recompress/inject may be the bug — report that; next is inject verification
on unmodified recompress with zero stubs.
