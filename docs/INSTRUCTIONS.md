# Task: Bisect — test commit 909c4bb (last untested commit before 6ba3f34)

## Why

The `--swap-order` diagnostic is **disproven**: `6ba3f34-repro-swapped.bin`
(manip-movies applied before single-disc, matching the production
builder's `addonApplyRank` fix) still shows the same broken transition —
disc 2, no break scene, no music — identical to the non-swapped build.
Makou save still works fine. So this is a **real regression** in the
commit range, not a test-harness apply-order artifact.

Separately, the first `909c4bb` build attempt failed its internal
CANONON check. Root cause: a bug in the repro harness itself
(`repoint_stale_layer_paths` in `build_aug7_repro.py`) — it always
redirected to the *latest* movies layer on disk even when the commit's
own hardcoded version still existed, pairing `909c4bb`'s pre-fix core
layer (v0.1.22) with a newer movies layer (v0.1.4) it was never tested
against. Fixed: it now only repoints when the commit's pinned version
was actually purged from `builder/`. Rebuilt successfully with the
correct pairing (core v0.1.2, movies v0.1.2, matching the literal
strings in that commit's own script).

Current state of the disc-2-prompt/no-break-scene bisection:
- `78e2cff` (v0.1.21): **GOOD** — straight to break scene, music present.
- `909c4bb` (v0.1.22): **UNTESTED** (only remaining commit in range).
- `cc87303` (v0.1.23): unbuildable standalone (CANONON mismatch) — skip.
- `6ba3f34` (v0.1.24): **BROKEN**, confirmed with and without swap order.
- `8e1f569`: **BROKEN**.
- `a6a14df`: **BROKEN** (disc-2 prompt, but does still show a save
  prompt — a milder variant than 6ba3f34/8e1f569/main).

This step tests `909c4bb` ("single-disc-on-csr-v0.1.22: restore MD8_52
NRCRL Cloud-position FMV") — the only remaining untested commit between
known-good `78e2cff` and known-bad `6ba3f34`. If broken, `909c4bb` itself
is the regression commit. If good, the bug is somehow specific to
`6ba3f34`'s changes despite the swap not fixing it (unlikely, but would
need a closer diff read).

The build isn't committed (`.bin` files are gitignored) — you rebuild it
locally with the commands below. It produces
`workspace/iso-extract/909c4bb-repro.bin`.

## Prerequisites

- `workspace/pristine/FINALFANTASY7_D1.bin`, `_D2.bin` present.
- `Final-Fantasy-7-CSR` repo checked out as a sibling of this repo at
  `/Users/david.morton/Final-Fantasy-7-CSR`.
- Python 3 on PATH; run all commands from this repo's root.

## What you do

1. `git pull --ff-only`.
2. Build `909c4bb-repro.bin`:

   ```bash
   python3 mods/single-disc/scripts/build_aug7_repro.py 909c4bb
   ```

   This creates a throwaway git worktree at that commit, runs *that*
   commit's own `build_playtest_bin.py` against your current pristine
   discs and CSR repo, copies the result back, and cleans up the
   worktree. Expect a `WROTE
   .../workspace/iso-extract/909c4bb-repro.bin (766,340,400 bytes)` line
   at the end with no `FAIL:` lines. If anything differs, paste full
   output before playtesting.

3. Open `workspace/iso-extract/909c4bb-repro.cue` in DuckStation fresh
   (no save states, no cheats).
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

- If the transition is **correct** on `909c4bb` (break scene + music):
  `909c4bb` is good, and the regression must be introduced by `6ba3f34`
  itself despite the apply-order swap not fixing it — needs a closer
  read of `6ba3f34`'s actual diff (LBA allocation changes) rather than
  apply order.
- If the bug **reproduces** on `909c4bb`: `909c4bb` is the regression
  commit — done bisecting the disc-2-prompt bug, move to reading its
  diff for the root cause.

## When done

Paste evidence above, commit this file, push, say check.
