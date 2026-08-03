# Task: No-swap — retest FIELD stubs v3 (full completion)

## What failed (already known — do not re-run v2)

- v1 jr-ra: black screen (no script PC advance)
- v2 PC+ only: movie **audio** on black screen, then no first field
  (MOVIE multi-frame state not cleared)

Older check paste was **v2** tool output (PC+1 / PC+2). Ignore for v3.

## v3 (current tool on main)

MOVIE completion stub at entry:
- clear entity byte@1 + half@38
- script PC += 1
- clear flags 0x80071C1C + 0x801144D4
- return 0

DSKCG: clear entity state + PC += 2 + return 0

Tool output should say **complete-stub** (not only PC+1 / PC+2).

## Apply (must git pull first)

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
cp -f workspace/pristine/FINALFANTASY7_D1.bin workspace/iso-extract/ff7_d1_noswap_work.bin
python3 mods/no-swap/scripts/stub_field_movie_dskcg.py \
  --disc-image workspace/iso-extract/ff7_d1_noswap_work.bin \
  --in-place
```

Confirm lines like:
`MOVIE @ 0x2CE94: 80B complete-stub` and `DSKCG ... 64B complete-stub`

## Playtest (critical)

1. **New game** — must reach Midgar / first field (not stuck black after intro)
2. Intro FMV — skip or no softlock after any audio
3. Optional disc-change hub save

## Evidence

```
git log -1 --oneline:
Tool output (v3 complete-stub lines):
New game reaches field: PASS/FAIL
Intro behavior:
Notes:
```

Say **check**.
