# Task: Diagnostic — test 6ba3f34 with movies-before-single-disc apply
# order (--swap-order)

## Why

Bisection hit a dead end: `909c4bb` and `cc87303` both fail to build
standalone (CANONON mismatch), so the only testable commits between
`78e2cff` (good) and `a6a14df` (bad) were the endpoints, plus `6ba3f34`
and `8e1f569` (both reproduce the bug: transition to disc 2 with no
break scene, no music).

Investigating `6ba3f34`'s own finding doc
(`docs/findings/2026-08-13-path-fmv-movies-pack-clobber.md`) revealed the
likely real cause: it documents that the **manip-movies pack must be
applied before the single-disc pack**, not after, because the movies
pack rewrites shared JAIROFAL/MOVIE_ID LBAs that the single-disc path
injects rely on. The documented fix was to change the **production
builder's** `addonApplyRank` (movies=10, single-disc-on-csr=20).

However, `mods/single-disc/scripts/build_playtest_bin.py` — the
standalone dev script this whole bisection has been using — was **never
updated** to match that reordering. It still hardcodes CSR → single-disc
→ movies on every commit, including current `main`. That means every
"disc-2-prompt / no break scene" result from `78e2cff` onward via this
script may be a **test-harness artifact**, not a bug present in the real
web builder players actually use.

This step tests that theory directly: rebuild `6ba3f34` with the apply
order swapped (movies applied first, single-disc second) using a new
`--swap-order` diagnostic flag. The internal CANONON check already
passes with this order. If the break scene/music now work in-game too,
the entire disc-2-prompt "regression" chase has been chasing a dev-script
bug, not a real one — and the real single-disc mod may never have been
broken in the shipped builder pack for these versions.

The build isn't committed (`.bin` files are gitignored) — you rebuild it
locally with the commands below. It produces
`workspace/iso-extract/6ba3f34-repro-swapped.bin` (808,951,584 bytes).

## Prerequisites

- `workspace/pristine/FINALFANTASY7_D1.bin`, `_D2.bin` present.
- `Final-Fantasy-7-CSR` repo checked out as a sibling of this repo at
  `/Users/david.morton/Final-Fantasy-7-CSR`.
- Python 3 on PATH; run all commands from this repo's root.

## What you do

1. `git pull --ff-only`.
2. Build `6ba3f34-repro-swapped.bin` (movies applied before single-disc):

   ```bash
   python3 mods/single-disc/scripts/build_aug7_repro.py 6ba3f34 --swap-order
   ```

   This creates a throwaway git worktree at that commit, patches that
   commit's own `build_playtest_bin.py` to apply manip-movies *before*
   the single-disc main pack, runs it against your current pristine
   discs and CSR repo, copies the result back, and cleans up the
   worktree. Expect a `WROTE
   .../workspace/iso-extract/6ba3f34-repro-swapped.bin (808,951,584
   bytes)` line at the end with no `FAIL:` lines. If anything differs,
   paste full output before playtesting.

3. Open `workspace/iso-extract/6ba3f34-repro-swapped.cue` in DuckStation
   fresh (no save states, no cheats).
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

- If the transition is **correct** with `--swap-order` (break scene +
  music): the whole `78e2cff..a6a14df` "regression" was a test-harness
  artifact — `build_playtest_bin.py` uses the wrong apply order, and the
  real production builder (which uses `addonApplyRank` from the
  `6ba3f34` fix) was never actually broken. In that case we'd stop
  chasing this as a code regression and instead fix/retire the dev
  script's hardcoded order.
- If the bug **still reproduces** even with movies-before-single-disc:
  the harness theory is wrong, and there's a real regression somewhere
  in `78e2cff..a6a14df` that isn't explained by apply order alone —
  resume bisecting `909c4bb` (only remaining untested commit; `cc87303`
  is unbuildable).

## When done

Paste evidence above, commit this file, push, say check.
