# Task: Bisect — test commit a6a14df (v0.1.25 boot fix, midpoint of
# dc24cb1..a6b800a)

## Why

Two separate regressions are being tracked, since they diverged between
`a6b800a` and `main`:

- **Disc-2-prompt regression**: on `11d6a8d` the D1→D2 transition goes
  straight to the break scene (correct single-disc behavior, no disc-swap
  prompt). On `a6b800a` it now shows "insert disc 2" before the break
  scene (wrong — regressed). On current `main` it's worse still: no save
  prompt at all, straight to black screen. Confirmed **absent** (works
  correctly) on `dc24cb1` — so the regression is somewhere in
  `dc24cb1..a6b800a` (29 commits).
- **Makou save regression**: works fine on both `11d6a8d` and `a6b800a`,
  but fails with "Invalid archive" on current `main`. So this one was
  introduced somewhere in `a6b800a..main` — bisect that range separately
  once the disc-2-prompt regression is found.

This step narrows the disc-2-prompt regression's origin by testing the
midpoint of `dc24cb1..a6b800a`: commit `a6a14df` ("Fix v0.1.25 boot: keep
MOVIE_ID at LBA 126959 - no EOF seek 80:52:34").

The build isn't committed (`.bin` files are gitignored) — you rebuild it
locally with the commands below. It produces
`workspace/iso-extract/a6a14df-repro.bin` (855,619,968 bytes — larger than
earlier builds because path-engine v0.1.25 layer content differs; that's
expected, not a build error).

## Prerequisites

- `workspace/pristine/FINALFANTASY7_D1.bin`, `_D2.bin` present.
- `Final-Fantasy-7-CSR` repo checked out as a sibling of this repo at
  `/Users/david.morton/Final-Fantasy-7-CSR`.
- Python 3 on PATH; run all commands from this repo's root.

## What you do

1. `git pull --ff-only`.
2. Build `a6a14df-repro.bin`:

   ```bash
   python3 mods/single-disc/scripts/build_aug7_repro.py a6a14df
   ```

   This creates a throwaway git worktree at that commit, runs *that*
   commit's own `build_playtest_bin.py` against your current pristine
   discs and CSR repo, copies the result back, and cleans up the
   worktree. Expect a `WROTE
   .../workspace/iso-extract/a6a14df-repro.bin (855,619,968 bytes)` line
   at the end with no `FAIL:` lines. If anything differs, paste full
   output before playtesting.

3. Open `workspace/iso-extract/a6a14df-repro.cue` in DuckStation fresh (no
   save states, no cheats).
4. New game, play through Midgar to confirm baseline sanity (no hangs).
5. Progress to the Disc 1→2 transition (BLACKBGB field #103 → LOST2 →
   break scene → COS_BTM2). Confirm exactly what happens, in order:
   - Does it ask "do you want to save?" (expected/normal on all builds).
   - After that, does it go straight to the break scene, or does it show
     an "insert disc 2" prompt first (the bug being tracked)?
   - Break scene plays with music, or black screen/silence?
6. Open this bin in Makou Reactor, make a trivial edit (e.g. rename a
   variable), Save. Confirm: succeeds, or fails with "Invalid archive"
   (or a different error — note exact text). Not expected to fail here
   (both `11d6a8d` and `a6b800a` save fine) but confirm anyway.

## Evidence (paste)

```
Disc 1→2 transition: straight to break scene (correct) / asks for disc 2 first (bug) / black screen no save prompt (main's worse bug)
Music: present / absent
Makou save test: SUCCEEDED / FAILED "Invalid archive" / FAILED other (paste exact text)
notes:
```

## Why this matters

- If the disc-2-prompt bug is **absent** on `a6a14df` (goes straight to
  break scene): the regression is in `a6a14df..a6b800a`, bisect further
  within that range.
- If the disc-2-prompt bug **reproduces** on `a6a14df`: the regression is
  in `dc24cb1..a6a14df`, bisect within that range instead.

## When done

Paste evidence above, commit this file, push, say check.
