# v0.2.8 New Game hang: disc1.layer.json shipped a corrupted FIELD.BIN

**Date:** 2026-08-23
**Confidence:** confirmed
**Status:** fixed (v0.2.9)
**Related:** docs/findings/2026-08-23-blackbgb-splice-lost2-lzs-fix-verified.md

## Summary

The published `single-disc-on-csr` v0.2.8 layer hung the game at "New Game"
on both the browser builder's own output and any local reconstruction of
the same stack. Root cause: `FIELD/FIELD.BIN` in the layer decompressed to
an invalid DEFLATE stream (`zlib.error: Error -3 ... invalid literal/lengths
set`). Since FIELD.BIN is read to load every field including the first one,
this broke the game before it could even reach the BLACKBGB/LOST2 content
that v0.2.8's release notes focused on — those fixes were correct and
unaffected.

## Discovery

Diffing the byte-identical (payload-wise) builder-site download against a
locally reconstructed builder-equivalent `.bin` showed 0 differences outside
EDC/ECC, so the corruption was in the checked-in layer itself, not a builder
site regression. Extracting `FIELD/FIELD.BIN` from the reconstructed image
and attempting `gzip.decompress()` on its GZIPPS payload threw the DEFLATE
error directly.

Isolating each pipeline step (`build_work_bin.py`'s rework merge, safe-field
merge, DSKCG removal/BLACKBGB splice, `fix_field_bin_table.py`, SNOVA
inject) confirmed a **freshly run** `build_work_bin.py` produces a
FIELD.BIN that decompresses correctly end-to-end. But the *published*
`disc1.layer.json`, when applied onto the CSR v0.14.2 base, produced a
different (corrupted) FIELD.BIN than that known-good work bin — despite
both being nominally "v0.2.8". This is the same failure mode as the
v0.1.3→v0.1.3.1 bug (`docs/findings/` history, see `31a5268`): the release
layer was diffed against a stale/broken intermediate build rather than the
actual verified pipeline output, so a corrupted byte silently shipped.

## Fix

First attempt: regenerated `disc1.layer.json` by running
`bin_diff_to_layer.py` against a freshly-built, flag-less `build_work_bin.py`
output. This fixed FIELD.BIN/WORLD.BIN decompression but **silently
reintroduced the D1→D2 BLACKBGB hang** — a flag-less run falls back to the
automated DSKCG-removal re-encoder (`apply_dskcg_removal`), which is still
broken (see `2026-08-23-blackbgb-splice-lost2-lzs-fix-verified.md`), instead
of `--blackbgb-manual-bin`'s verified manual splice. The manual-edit
`BLACKBGB.DAT` source is gitignored and wasn't available locally to re-supply
that flag. Confirmed via byte comparison: the flag-less rebuild's
`FIELD/BLACKBGB.DAT` was 13,011 bytes vs the verified splice's 13,013 bytes —
different content, not just size-adjacent.

Actual fix: built a **hybrid** image instead of a full flag-less rebuild.
1. Reconstructed the (corrupted) v0.2.8 image by applying the checked-in
   v0.2.8 layer onto the CSR v0.14.2 base, and confirmed its
   `FIELD/BLACKBGB.DAT` (13,013 bytes) decompresses fine and is the known
   verified splice — only `FIELD.BIN` was broken in v0.2.8.
2. Extracted the corrected `FIELD/FIELD.BIN` and `WORLD/WORLD.BIN` from the
   freshly-built (flag-less) work bin, and spliced *only those two files*
   into the reconstructed v0.2.8 image via `replace_file_within_sectors`,
   leaving `BLACKBGB.DAT` and everything else from v0.2.8 untouched.
3. Re-diffed this hybrid image against the CSR v0.14.2 base with
   `bin_diff_to_layer.py` to produce the new `disc1.layer.json`.

Verified the new layer, reapplied onto CSR v0.14.2 via `apply_layer.py`,
reproduces the hybrid image **byte-for-byte**. `FIELD.BIN`/`WORLD.BIN`
decompress correctly; `FIELD/BLACKBGB.DAT` byte-identical to the verified
v0.2.8 splice. Swept all 787 `FIELD/*.DAT` files for LZS decompression
failures — 73 fail, and the *same* 73 fail on a plain reconstructed v0.2.8
image too (non-LZS files, e.g. `WM*.DAT` world map textures), confirming
this is a pre-existing, unrelated baseline and not a regression.

Released as v0.2.9. Record counts: base csr-v0.14.2 87,606 + addon
single-disc-on-csr 63,712 = 151,318 total.

## Why it matters

Any future release of this mod (or any mod using the rebuild-from-scratch
`build_work_bin.py` → `bin_diff_to_layer.py` pattern) must diff the
**actual verified work bin that was playtested**, not a rebuild assumed to
be equivalent. A cheap sanity check going forward: after generating any
layer, apply it onto the base image and confirm `FIELD.BIN`/`WORLD.BIN`
(and any other GZIPPS-compressed archive touched) still decompress before
publishing.

## Follow-ups

- [ ] Consider adding an automated check to the release pipeline: after
      `bin_diff_to_layer.py`, reapply the layer and assert `FIELD.BIN`/
      `WORLD.BIN` decompress and the reconstructed image matches the source
      work bin byte-for-byte.
- [ ] Save the manual-edit `BLACKBGB.DAT` (or the working `.bin` it was
      pulled from) somewhere durable/tracked (outside the gitignored
      workspace) so a future flag-less `build_work_bin.py` run doesn't
      silently drop the D1→D2 fix again.
- [x] Playtest v0.2.9 (hybrid layer) past New Game through the D1→D2
      transition on DuckStation — confirmed working locally.
- [ ] Confirm the builder-site download of v0.2.9 also passes
      `verify_built_disc.py` and plays through New Game + D1→D2 in
      DuckStation (local reconstruction confirmed; site download pending).
- [ ] Confirm on real PSX hardware (still outstanding from v0.2.8).

## Sources

- `scripts/bin_diff_to_layer.py`, `scripts/apply_layer.py`,
  `psx_mode2_iso.replace_file_within_sectors`
- `mods/single-disc/scripts/build_work_bin.py`,
  `mods/single-disc/scripts/fix_field_bin_table.py`
- `builder/single-disc-on-csr/layers/disc1.layer.json` (hybrid regeneration)
- commits `3f63bff` (flawed first attempt), hybrid fix (this session)
