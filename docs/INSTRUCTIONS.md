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

Build succeeded cleanly (script's own internal CANONON/LBA-alias checks
passed). Output copied to:

- `workspace/iso-extract/aug7-repro.bin` (766,340,400 bytes)
- `workspace/iso-extract/aug7-repro.cue`

## What you do

1. `git pull --ff-only`.
2. Open `workspace/iso-extract/aug7-repro.cue` in DuckStation fresh (no
   save states, no cheats).
3. New game, play through Midgar to confirm baseline sanity (no hangs).
4. Progress to the Disc 1→2 transition (BLACKBGB field #103 → LOST2 →
   break scene → COS_BTM2). Confirm exactly what happens:
   - Disc-swap prompt appears or not.
   - Break scene plays or black screen/silence.
   - Music present or absent.
5. Open this bin in Makou Reactor, make a trivial edit (e.g. rename a
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
