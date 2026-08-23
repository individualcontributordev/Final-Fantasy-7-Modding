# v0.2.9 hybrid layer corrupted LOST2's section table; fixed by rebuilding from scratch

**Date:** 2026-08-23
**Confidence:** confirmed (local reconstruction; DuckStation playtest pending)
**Status:** promoted
**Related:** docs/findings/2026-08-23-v028-new-game-hang-corrupted-field-bin-layer.md, docs/findings/2026-08-23-blackbgb-splice-lost2-lzs-fix-verified.md

## Summary

After v0.2.9's "want to save?" prompt on the D1→D2 transition, the Cosmo
Canyon break scene (LOST2, field 634) failed to load. `FIELD/LOST2.DAT` was
the correct 17,032-byte size (matching CSR D2) and still LZS-decompressed
without a hard error, but its internal 7-section offset table was wrong,
which Makou Reactor showed as a corrupted field.

## Context

v0.2.9 was built as a **hybrid layer**: to avoid rebuilding from scratch
(which required the gitignored/"unavailable" manual `FIELD/BLACKBGB.DAT`
splice), the known-good v0.2.8 image's `FIELD/BLACKBGB.DAT` was patched
onto a separately-fixed work bin's `FIELD.BIN`/`WORLD.BIN`, then the whole
thing was re-diffed against the CSR v0.14.2 base to produce
`disc1.layer.json`.

## Discovery

Comparing the shipped `FIELD/LOST2.DAT` against CSR D2's own file:

- Same length (17,032 bytes) and both LZS-decompress without exception.
- Section sizes differed: shipped `{walkmesh: 3740, background: 13268,
  model_loader: 2348}` vs CSR D2's correct `{walkmesh: 3996,
  background: 13012, model_loader: 76}`.
- Byte-for-byte diff against CSR D2 showed 331 scattered differing bytes
  across nearly the whole file — not a simple truncation/pad issue.
- A fresh, non-hybrid `build_work_bin.py` run (no manual stitching)
  produced a `FIELD/LOST2.DAT` byte-identical to CSR D2 with correct
  section sizes, isolating the corruption to the hybrid-stitch step
  itself, not `merge_safe_fields.py`'s whole-file LOST2 swap (which is
  a verbatim byte copy and was already correct).

## Root cause

The hybrid stitch's ad-hoc byte-range patching (from an interactive session,
not a repeatable script) miscopied or misaligned bytes into LOST2's region
while combining the two source images. The exact step wasn't preserved
(it was done manually, not via a committed script), so it isn't
reproducible from history — but the fresh single-pass rebuild avoids the
whole class of bug by construction.

## Fix

1. Recovered the "unavailable" manual `FIELD/BLACKBGB.DAT` splice from a
   prior commit (`fb2f9b3`, briefly tracked before being gitignored) and
   committed it permanently at `mods/single-disc/patches/BLACKBGB.manual.dat`.
2. Made `build_work_bin.py --blackbgb-manual-bin` default to that committed
   path, so a plain flag-less run no longer silently falls back to the
   broken automated DSKCG re-encoder.
3. Ran `build_work_bin.py` once, end-to-end (rework merge → safe-field
   merge → BLACKBGB manual splice → FIELD.BIN/WORLD.BIN table fix → SNOVA
   inject) with no manual post-processing.
4. Diffed the result directly against the CSR v0.14.2 base into a fresh
   `disc1.layer.json` (63,419 addon records, down from v0.2.9's
   hybrid-stitched 63,712) via `bin_diff_to_layer.py`.
5. Verified via `scripts/apply_layer.py --expect`: reapplying the new layer
   onto the CSR base reproduces the work bin byte-for-byte.
6. Verified via `scripts/verify_builder_config.py` (the real base+addon
   stacking path used by the site): `FIELD/LOST2.DAT` byte-identical to
   CSR D2 (correct section sizes restored), `FIELD/BLACKBGB.DAT`
   byte-identical to the verified manual splice.
7. Swept all 787 `FIELD/*.DAT` files for LZS/parse errors: 82 fail on both
   the plain CSR-only base and this addon stack (pre-existing non-LZS
   files) — no new failures introduced.

Released as **v0.2.10**.

## Why it matters

Confirms the general lesson from the v0.2.8→v0.2.9 fix: **any hand-stitched
or manually-patched layer/image, done outside a repeatable script, is a
regression risk** — even when the total file size matches a known-good
reference. Rebuilding from a single scripted pipeline and diffing once is
the reliable path.

## Follow-ups

- [ ] Playtest v0.2.10 past the break scene on DuckStation.
- [ ] Playtest on real PSX hardware.
- [ ] Investigate why the Okumura-encoded BLACKBGB still hangs post-DSKCG-
      removal (would let us drop the manual-splice dependency entirely —
      tracked in the LZS-fix finding above).

## Sources

- `mods/single-disc/scripts/build_work_bin.py`
- `mods/single-disc/scripts/merge_safe_fields.py`
- `mods/single-disc/patches/BLACKBGB.manual.dat` (newly committed)
- `scripts/bin_diff_to_layer.py`, `scripts/apply_layer.py`,
  `scripts/verify_builder_config.py`
