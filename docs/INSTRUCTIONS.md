# Task: Test the Aug 6/7 build state (pre-FIELD.BIN-table-fix, pre-ending-credits)

## Why

Both current bugs (Disc 1→2 black screen/no music, Makou "Invalid archive"
on save) were never documented in the week before Aug 7, and the FIELD.BIN
table-corruption fix and the LOST2 IFUW break-scene work are both *later*
discoveries (Aug 11+ and this week respectively). To find out whether these
bugs already existed back then (i.e. are old/pre-existing, not caused by
recent work), I rebuilt the exact bin that commit `11d6a8d` (2026-08-06
22:30, last commit before the Aug 7 ending-credits work started) would have
produced, using that commit's own `build_playtest_bin.py` script and layers
(CSR v0.14.1 base + `single-disc-on-csr-v0.1.2` + cumulative
`single-disc-csr-manip-movies-v0.1.2`). No FIELD.BIN table fix, no LOST2
IFUW force — this is what shipped/was tested that week, unmodified.

The build isn't committed (`.bin` files are gitignored) — you rebuild it
locally with the commands below. Build succeeds cleanly (script's own
internal CANONON/LBA-alias checks pass) and produces a 766,340,400-byte
bin named `aug7-repro.bin`.

## Prerequisites

- `workspace/pristine/FINALFANTASY7_D1.bin`, `_D2.bin` present.
- `Final-Fantasy-7-CSR` repo checked out as a sibling of this repo at
  `/Users/david.morton/Final-Fantasy-7-CSR`.
- Python 3 on PATH; run all commands from this repo's root.

## What you do

1. `git pull --ff-only`.
2. Build `aug7-repro.bin` from the pinned Aug 6 commit (`11d6a8d`, the
   last commit before the Aug 7 ending-credits work started):

   ```bash
   git worktree add /tmp/ff7-aug7-build 11d6a8d
   mkdir -p /tmp/ff7-aug7-build/workspace/pristine
   for f in workspace/pristine/*.bin; do ln -sf "$(pwd)/$f" "/tmp/ff7-aug7-build/$f"; done
   ln -sf /Users/david.morton/Final-Fantasy-7-CSR /private/tmp/Final-Fantasy-7-CSR
   cd /tmp/ff7-aug7-build
   python3 mods/single-disc/scripts/build_playtest_bin.py
   cd /Users/david.morton/Final-Fantasy-7-Modding
   mkdir -p workspace/iso-extract
   cp /private/tmp/ff7-aug7-build/workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.bin workspace/iso-extract/aug7-repro.bin
   cp /private/tmp/ff7-aug7-build/workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.cue workspace/iso-extract/aug7-repro.cue
   sed -i '' 's/ff7_d1_playtest_csr_sd_movies.bin/aug7-repro.bin/' workspace/iso-extract/aug7-repro.cue
   git worktree remove /tmp/ff7-aug7-build --force
   rm -f /private/tmp/Final-Fantasy-7-CSR
   ls -la workspace/iso-extract/aug7-repro.*
   ```

   Expect the build script to print `WROTE .../ff7_d1_playtest_csr_sd_movies.bin`
   with no `FAIL:` lines, and the final `ls` to show `aug7-repro.bin` at
   766,340,400 bytes. If anything differs, paste full output before
   playtesting.

3. Open `workspace/iso-extract/aug7-repro.cue` in DuckStation fresh (no
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

- If **both bugs already reproduce** on this Aug-6/7-era bin: they are old,
  pre-existing issues unrelated to the ending-credits work, the FIELD.BIN
  table fix, or the LOST2/IFUW break-scene work done since — the real root
  cause is still further back (predates this window) or is structural to
  the single-disc approach itself (e.g. `single-disc-on-csr-v0.1.2` pack
  content, not later regressions).
- If the transition or save **worked correctly** on this old bin: the bug
  was introduced somewhere between Aug 6 and now, and we can bisect forward
  commit-by-commit from `11d6a8d`.

## When done

Paste evidence above, commit this file, push, say check.
