# Task: Smoke BATRES skip ceremony setup block

## Previous results (recorded)

### s4=0 only
- Fanfare + win anims still start on kill
- Immediate black to rewards; fanfare plays over rewards page

### s4=0 + nop jal 800A7254 @ 801B028C
- **Animations still there** (operator)
- So type-4 queue seed is **not** required for win poses (or something else re-seeds them)

Finding: [findings/2026-08-09-fanfare-skip-015-gap-ceremony-still-plays.md](findings/2026-08-09-fanfare-skip-015-gap-ceremony-still-plays.md)

## Why this smoke

Ghidra setup between `801B02E0` and `801B03B0` does more than the 7254 jal:

- `sb` actor mode bytes **0xC** / **0xE** (pose-related)
- sets `DAT_800fa6b8` / `DAT_80163b80`
- sets wait s4

Stock already has: if flag bit8 set, **skip that whole block** (`bne` to `801B03B0`).

**This patch:** force that skip always: `801B02E0` -> `j 801B03B0`  
Also keep s4=0 + nop 7254 so wait/seed stay out of the way.

## Build (no heredoc)

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
python3 scripts/build_batres_ceremony_smoke.py --skip-setup --s4-zero --no-anim4
```

Expect: `PLAY: .../ff7_d1_batres_skipsetup_s4zero_noanim4.bin`

## Play

1. DuckStation Open Image `workspace/iso-extract/ff7_d1_batres_skipsetup_s4zero_noanim4.bin`
2. Win one normal random battle (pristine; not 0.1.5 stack).

## Evidence (fill in)

```
Image: ff7_d1_batres_skipsetup_s4zero_noanim4.bin
Patches: j 801B03B0 @ 801B02E0 + s4=0 + nop 7254

After last enemy dies:
  fanfare audible: YES/NO
  win poses / victory dance: YES/NO / SHORTER / NONE
  immediate black to rewards: YES/NO
  fanfare continues on rewards page: YES/NO / N/A
  freeze or hang: YES/NO
  can leave battle to field: YES/NO

Compared to noanim4-only:
  poses different?:
  music different?:

notes:
```

## When done

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
git add docs/INSTRUCTIONS.md
git commit -m "ops: smoke BATRES skip-setup ceremony block"
git push
```

Then say **check**.

Do **not** commit the .bin image.

## Refs

- Builder: `scripts/build_batres_ceremony_smoke.py`
- Pastes: [ghidra-pastes/batres-victory-path.md](ghidra-pastes/batres-victory-path.md)
