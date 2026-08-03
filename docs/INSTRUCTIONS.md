# Task: No-swap — retest FIELD stubs v4 (no entity writes)

## Failures so far

| Ver | Behavior |
|-----|----------|
| v1 jr-ra | black, no progress |
| v2 PC++ only | audio + black, no field |
| v3 PC++ + entity* clear | same (entity ptr may be invalid at intro) |

## v4 theory

Original MOVIE has a fast path that **only** does PC+=1 + return (no entity stores).
v3 always wrote entity+1 / +38 via *(0x8009C6E0) — dangerous if null/wrong during boot intro.

v4: **script PC += size + clear flags + return 0**. No entity pointer loads.

## Apply

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
cp -f workspace/pristine/FINALFANTASY7_D1.bin workspace/iso-extract/ff7_d1_noswap_work.bin
python3 mods/no-swap/scripts/stub_field_movie_dskcg.py \
  --disc-image workspace/iso-extract/ff7_d1_noswap_work.bin \
  --in-place
```

Tool lines should say **v4 no-entity**.

## Playtest

1. New game → first field? PASS/FAIL
2. If still audio on black: note duration; does field ever appear after?
3. If still FAIL: stop tool experiments for now — next is different approach
   (e.g. only skip low-level stream start, leave handler body alone)

## Evidence

```
Tool output (must say v4):
New game reaches field: PASS/FAIL
Intro:
Notes:
```

Say **check**.

 Final-Fantasy-7-Modding git:(main) cp -f workspace/pristine/FINALFANTASY7_D1.bin workspace/iso-extract/ff7_d1_noswap_work.bin
python3 mods/no-swap/scripts/stub_field_movie_dskcg.py \
  --disc-image workspace/iso-extract/ff7_d1_noswap_work.bin \
  --in-place
DSKCG @ 0x2523C: 64B v4 no-entity (was 0a80023c20d84290)
MOVIE @ 0x2CE94: 64B v4 no-entity (was 0a80023c20d84290)
recompressed FIELD.BIN 85435 -> 85373 (slot 85435)
wrote workspace\iso-extract\ff7_d1_noswap_work.bin


still the same, black screen, movie sounds of intro no visuals, field does not load after, intro is probably 1 min 30 secs long