# Task: Playtest single-disc-on-csr v0.2.2 (fixes v0.2.1 black screen)

## Why

Root cause of the v0.2.1 black-screen regression found: `build_work_bin.py`
was live-stripping DSKCG ("Ask for disc") ops from BLACKBGB/BLACKBGE/
BLACKBG3 via `remove_dskcg.py`, but that splicer produces a field that
diverges from the **proven-working v0.1.2 field** by ~12k bytes after
decompression — it was corrupting BLACKBGB, which is the field the
player is standing in right before the D1→D2 transition, causing the
hang before LOST2 (and its IFUW gate fix) is ever reached.

Fixed in `build_work_bin.py`: it now injects the pre-exported,
DSKCG-stripped fields from `workspace/v012-exports/` (byte-identical to
the field that shipped working in v0.1.2) instead of running the live
splicer. Verified:
- Rebuilt work bin's BLACKBGB/BLACKBGE/BLACKBG3 are byte-identical to
  `workspace/v012-exports/*.DAT`.
- Re-diffed into `disc1.layer.json`, round-trips byte-for-byte against
  a fresh CSR D1 base.
- `verify_builder_config.py --base csr-v0.14.1 --addon single-disc-on-csr`
  passes end-to-end and the resulting stack also has the correct
  BLACKBGB/E/3 bytes.

Bumped to **v0.2.2**. This is a fresh playtest — confirm all three
issues (D1→D2 transition, music, Makou save) are actually fixed on the
real shipped pack.

The build isn't committed (`.bin`/`.cue` gitignored) — rebuilt locally
below. Produces `workspace/iso-extract/single-disc-v022-repro.bin`
(748,775,664 bytes).

## Prerequisites

- `workspace/pristine/FINALFANTASY7_D1.bin`, `_D2.bin`, `_D3.bin` present.
- `Final-Fantasy-7-CSR` repo checked out as a sibling of this repo.
- Python 3 on PATH; run all commands from this repo's root.

## What you do

1. `git pull --ff-only`.
2. Rebuild the work bin and a matching `.cue`:

   ```bash
   python3 mods/single-disc/scripts/build_work_bin.py -o workspace/iso-extract/single-disc-v022-repro.bin
   printf 'FILE "single-disc-v022-repro.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > workspace/iso-extract/single-disc-v022-repro.cue
   ```

   Expect `Injecting pre-exported DSKCG-stripped fields ... for
   ['BLACKBGB', 'BLACKBGE', 'BLACKBG3']` then `Wrote
   workspace/iso-extract/single-disc-v022-repro.bin (747,435,024 bytes)
   [pre-SNOVA]` then `Done. Final work bin: ...` with the final file at
   **748,775,664 bytes**. No `WARNING:` or uncaught errors.

3. Open `workspace/iso-extract/single-disc-v022-repro.cue` in
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
