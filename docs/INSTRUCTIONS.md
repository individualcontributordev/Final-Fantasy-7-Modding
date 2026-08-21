# Task: Bisect — test commit a6b800a (single-disc v0.1.35, roughly midway
# between confirmed-good 11d6a8d and current main)

## Why

Confirmed on `11d6a8d` (2026-08-06 22:30): both bugs (Disc 1→2 black
screen/no music, Makou "Invalid archive" on save) are **absent** — that
build worked correctly. So the regression is somewhere in the 116 commits
between `11d6a8d` and `main` that touch `mods/single-disc/` or `scripts/`.
This step tests the midpoint, `a6b800a` ("single-disc v0.1.35: LOST2 forest
music unmute; retire v0.1.34"), to narrow down which half of the range
contains the bug.

The build isn't committed (`.bin` files are gitignored) — you rebuild it
locally with the commands below. It produces `workspace/iso-extract/a6b800a-repro.bin`
(766,970,736 bytes).

## Prerequisites

- `workspace/pristine/FINALFANTASY7_D1.bin`, `_D2.bin` present.
- `Final-Fantasy-7-CSR` repo checked out as a sibling of this repo at
  `/Users/david.morton/Final-Fantasy-7-CSR`.
- Python 3 on PATH; run all commands from this repo's root.

## What you do

1. `git pull --ff-only`.
2. Build `a6b800a-repro.bin`:

   ```bash
   python3 mods/single-disc/scripts/build_aug7_repro.py a6b800a
   ```

   This creates a throwaway git worktree at that commit, runs *that*
   commit's own `build_playtest_bin.py` against your current pristine
   discs and CSR repo, copies the result back, and cleans up the
   worktree. Expect a `WROTE
   .../workspace/iso-extract/a6b800a-repro.bin (766,970,736 bytes)` line
   at the end with no `FAIL:` lines. If anything differs, paste full
   output before playtesting.

3. Open `workspace/iso-extract/a6b800a-repro.cue` in DuckStation fresh (no
   save states, no cheats).
4. New game, play through Midgar to confirm baseline sanity (no hangs).
5. Progress to the Disc 1→2 transition (BLACKBGB field #103 → LOST2 →
   break scene → COS_BTM2). Confirm exactly what happens:
   - Disc-swap prompt appears or not.
   - Break scene plays or black screen/silence.
   - Music present or absent.
6. Open this bin in Makou Reactor, make a trivial edit (e.g. rename a
   variable), Save. Confirm: succeeds, or fails with "Invalid archive"
   (or a different error — note exact text).

## Evidence (paste)

```
Disc 1→2 transition: WORKED (music+scene) / BLACK SCREEN NO MUSIC / OTHER (describe)
Makou save test: SUCCEEDED / FAILED "Invalid archive" / FAILED other (paste exact text)
notes:
```

## Why this matters

- If **both work correctly** on `a6b800a`: the regression is in the second
  half of the range (`a6b800a..main`), and we bisect further within that
  half.
- If **either bug reproduces** on `a6b800a`: the regression is in the
  first half (`11d6a8d..a6b800a`), and we bisect within that half instead.

## When done

Paste evidence above, commit this file, push, say check.
