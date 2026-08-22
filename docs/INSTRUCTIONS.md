# Task: Playtest single-disc-on-csr v0.2.1 (both regressions fixed)

## Why

Both regressions this whole bisection was chasing are now believed fixed
on `main`, independently of the bisection:

1. **Disc 1→2 break-scene regression** (the `78e2cff..a6a14df` bug we were
   bisecting): `main` was rebuilt from scratch on Aug 21
   (`e45a5bf`, "v0.2.0") using a new `build_work_bin.py` pipeline that
   includes `force_lost2_break_ifuw.py` — explicitly forces LOST2's
   D1→D2 break-scene IFUW gate open, since the GM flag it checks is
   never set on single-disc.
2. **Makou Reactor "Invalid archive" save regression**: fixed this
   morning in `c3a420e` — `FIELD.BIN`/`WORLD.BIN` embed their own
   (location,size) lookup table per field, used by ff7tk's
   `reorganizeModifiedFilesAfter()` on every save. Field merges resized
   files but never updated that table, so any save failed. Fixed via
   `fix_field_bin_table.py`, wired into `build_work_bin.py` as a new
   step.

The **shipped** `builder/single-disc-on-csr/layers/disc1.layer.json`
(v0.2.0) predated the Makou-save fix (`e45a5bf` before `c3a420e`), so it
was rebuilt just now with the current pipeline and bumped to **v0.2.1**.
Verified: applying the new layer to a fresh CSR D1 base reproduces the
rebuilt work bin byte-for-byte.

This step is a **fresh playtest from scratch** (not another bisection
step) — confirm both bugs are actually gone on the real shipped pack.

The build isn't committed (`.bin`/`.cue` are gitignored) — it's rebuilt
locally below. Produces
`workspace/iso-extract/single-disc-v021-repro.bin` (748,775,664 bytes).

## Prerequisites

- `workspace/pristine/FINALFANTASY7_D1.bin`, `_D2.bin`, `_D3.bin` present.
- `Final-Fantasy-7-CSR` repo checked out as a sibling of this repo.
- Python 3 on PATH; run all commands from this repo's root.

## What you do

1. `git pull --ff-only`.
2. Rebuild the work bin and a matching `.cue` (regenerates the exact
   bytes already committed in the layer — `.bin`/`.cue` aren't tracked
   in git, this just gets you a local file to playtest):

   ```bash
   python3 mods/single-disc/scripts/build_work_bin.py -o workspace/iso-extract/single-disc-v021-repro.bin
   printf 'FILE "single-disc-v021-repro.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > workspace/iso-extract/single-disc-v021-repro.cue
   ```

   Expect `Wrote workspace/iso-extract/single-disc-v021-repro.bin
   (747,435,024 bytes) [pre-SNOVA]` then `Done. Final work bin: ...`
   with the final file at **748,775,664 bytes**. No `WARNING:` or
   uncaught errors.

3. Open `workspace/iso-extract/single-disc-v021-repro.cue` in
   DuckStation fresh (no save states, no cheats).
4. New game, play through Midgar to confirm baseline sanity (no hangs).
5. Progress to the Disc 1→2 transition (BLACKBGB field #103 → LOST2 →
   break scene → COS_BTM2). Confirm exactly what happens, in order:
   - Does it ask "do you want to save?" (expected/normal).
   - After that, does it go straight to the break scene (fixed), or
     show an "insert disc 2" prompt / black screen (bug still present)?
   - Break scene plays with music, or black screen/silence?
6. Open this bin in Makou Reactor, make a trivial edit (e.g. rename a
   variable), Save. Confirm: succeeds (fixed) or fails with "Invalid
   archive" / "Cannot update game binaries" (bug still present — note
   exact text).

## Evidence (paste)

```
Disc 1→2 transition: straight to break scene (fixed) / asks for disc 2 first (bug) / black screen no save prompt (bug)
Music: present / absent
Makou save test: SUCCEEDED (fixed) / FAILED "Invalid archive" (bug) / FAILED other (paste exact text)
notes:
```

## When done

Paste evidence above, commit this file, push, say check.
