# Task: Smoke BATRES s4=0 + nop anim type-4 seed

## Previous result (s4=0 only) - recorded

With wait counts forced to 0 only:

- Fanfare + win anims **still start** on kill (same as before)
- Screen **immediately** goes black to **rewards**
- Fanfare **plays in full on the rewards page**; rewards music after fanfare ends

So `s4` only held the ceremony; it does **not** start music/poses.
Finding: [findings/2026-08-09-fanfare-skip-015-gap-ceremony-still-plays.md](findings/2026-08-09-fanfare-skip-015-gap-ceremony-still-plays.md)

## This smoke

Same as s4=0 **plus** nop the win-anim seed:

| VA | Patch |
|----|-------|
| 801B02F8 / 032C / 03A0 | ori s4,0,0 (keep) |
| **801B028C** | `jal 800A7254` to `nop` |

That jal is the `FUN_800a7254(0, i, 4, 0)` x10 loop from Ghidra.

## Build (one command, no heredoc)

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
python3 scripts/build_batres_ceremony_smoke.py
```

Expect: `PLAY: .../ff7_d1_batres_s4zero_noanim4.bin`

## Play

1. DuckStation Open Image `workspace/iso-extract/ff7_d1_batres_s4zero_noanim4.bin`
2. Win one normal random battle (pristine path; not 0.1.5 stack).

## Evidence (fill in)

```
Image: ff7_d1_batres_s4zero_noanim4.bin
Patches: s4=0 + nop jal 800A7254 @ 801B028C

After last enemy dies:
  fanfare audible: YES/NO
  win poses / victory dance: YES/NO / SHORTER / NONE
  immediate black to rewards: YES/NO
  fanfare continues on rewards page: YES/NO / N/A
  rewards BGM after fanfare: YES/NO / N/A
  freeze or hang: YES/NO
  can leave battle to field: YES/NO

Compared to s4=0-only smoke:
  poses different?:
  music different?:

notes:
```

## When done

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
# fill Evidence above, then:
git add docs/INSTRUCTIONS.md
git commit -m "ops: smoke BATRES s4=0 + nop anim4 seed"
git push
```

Then say **check**.

Do **not** commit the .bin image.

## Refs

- Builder: `scripts/build_batres_ceremony_smoke.py`
- Pastes: [ghidra-pastes/batres-victory-path.md](ghidra-pastes/batres-victory-path.md)
