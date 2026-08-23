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

Regenerated `builder/single-disc-on-csr/layers/disc1.layer.json` by running
`bin_diff_to_layer.py` against a freshly-built `build_work_bin.py` output
(confirmed both `FIELD/FIELD.BIN` and `WORLD/WORLD.BIN` decompress
correctly beforehand). Verified the new layer, reapplied onto the CSR
v0.14.2 base via `apply_layer.py`, reproduces that work bin **byte-for-byte**
(`img == good` in Python). Also swept all 787 `FIELD/*.DAT` files for LZS
decompression failures in the new build — 73 fail, but the same 73 fail on
a plain CSR-only base too (non-LZS files, e.g. `WM*.DAT` world map
textures), so this is a pre-existing, unrelated baseline and not a
regression.

Released as v0.2.9. Record counts: base csr-v0.14.2 87,606 + addon
single-disc-on-csr 60,864 = 148,470 total (down from 152,892 combined in
the corrupted v0.2.8, consistent with the smaller/correct addon-only diff
of 60,864 vs the previous 72,788).

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
- [ ] Playtest v0.2.9 past New Game through the D1→D2 transition on
      DuckStation to reconfirm BLACKBGB/LOST2 fixes still hold with the
      regenerated layer (not yet done as of this finding).
- [ ] Confirm on real PSX hardware (still outstanding from v0.2.8).

## Sources

- `scripts/bin_diff_to_layer.py`, `scripts/apply_layer.py`
- `mods/single-disc/scripts/build_work_bin.py`,
  `mods/single-disc/scripts/fix_field_bin_table.py`
- `builder/single-disc-on-csr/layers/disc1.layer.json` (regenerated)
- commit `3f63bff`
