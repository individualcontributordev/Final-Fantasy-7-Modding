# Task: Smoke BATRES ceremony wait skip (s4=0)

## Why (from your Ghidra pastes — archived)

Clean decompiles: [ghidra-pastes/batres-victory-path.md](ghidra-pastes/batres-victory-path.md)

Finding update: [findings/2026-08-09-fanfare-skip-015-gap-ceremony-still-plays.md](findings/2026-08-09-fanfare-skip-015-gap-ceremony-still-plays.md)

In `batres_victory`:

1. Queue win anims: `FUN_800a7254(0, i, 4, 0)` x10
2. Normal path sets **wait count s4 = 0x31** (~49 frames) + flag `DAT_800fa6b8=1`
3. Loop `FUN_800a3354()` that many times (ceremony hold)
4. Then rewards (`800a56b0` …)

`800a7254` / `800a3354` / `80014540` are **not** the music engine.

**This smoke:** force all ceremony wait counts to **0** in BATRES only:

| VA | Stock | Patch |
|----|-------|-------|
| 801B02F8 | ori s4,0,0x1E | ori s4,0,**0** |
| 801B032C | ori s4,0,0x08 | ori s4,0,**0** |
| 801B03A0 | ori s4,0,0x31 | ori s4,0,**0** |

Recompressed GZIPPS fits original slot. Does **not** touch FAN2.SND.

Goal: see if skipping the wait still plays fanfare, still shows poses, and still reaches loot safely.

## Build play image

**One command — no heredoc.** Copy-paste these two lines only:

```bash
cd "$(git rev-parse --show-toplevel)"
python3 scripts/build_batres_s4zero_image.py
```

Expect last line: `PLAY: .../workspace/iso-extract/ff7_d1_batres_s4zero.bin`

If it errors about missing pristine disc, ensure
`workspace/pristine/FINALFANTASY7_D1.bin` exists.

## Play

1. DuckStation → Open Image → `workspace/iso-extract/ff7_d1_batres_s4zero.bin`
2. Clean/pristine battle (this image is **not** stacked with fanfare-skip 0.1.5).
3. Win one normal random battle.

## Evidence (fill in)

```
Image: ff7_d1_batres_s4zero.bin
Base: pristine D1 + BATRES s4 wait=0 only

After last enemy dies:
  fanfare audible: YES/NO
  win poses / victory dance: YES/NO / SHORTER
  freeze or hang: YES/NO
  rewards (exp/items) screen appears: YES/NO
  can leave battle to field: YES/NO

Compared to stock (if you know):
  ceremony shorter?: YES/NO/UNSURE
  anything broken?:

notes:
```

## When done

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
# edit Evidence above, then:
git add docs/INSTRUCTIONS.md
git commit -m "ops: smoke BATRES s4=0 ceremony wait skip"
git push
```

Then say **check**.

Do **not** commit the .bin image.

## Refs

- Builder script: `scripts/build_batres_s4zero_image.py`
- Ghidra setup: [ghidra-battle-overlays.md](ghidra-battle-overlays.md)
- Pastes: [ghidra-pastes/batres-victory-path.md](ghidra-pastes/batres-victory-path.md)

