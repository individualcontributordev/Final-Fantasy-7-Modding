# BLACKBGB manual-edit splice + bit-exact LZS encoder: both verified on DuckStation

**Date:** 2026-08-23
**Confidence:** likely
**Status:** promoted
**Related:** docs/findings/2026-08-16-blackbgb-pristine-no-mapjump.md, docs/findings/2026-08-13-lost2-break-bit-bank3-84.md

## Summary

The D1→D2 BLACKBGB transition hang and the LOST2 background corruption are
both fixed and confirmed working via DuckStation emulator playtest. Not yet
tested on real PSX hardware.

## Context

The automated DSKCG-removal splicer's own LZS re-encode of BLACKBGB kept
producing a black-screen hang on the D1→D2 transition, even though the
re-encoded script bytes matched a manual Makou Reactor edit byte-for-byte
and round-tripped through our own decompressor. LOST2's background was
separately corrupted after any field touching our LZS re-encoder.

## Discovery

Two independent fixes, both now playtest-confirmed:

1. **LZS encoder bug (root cause of LOST2 corruption)**: `scripts/lzs.py`
   was a from-scratch LZSS encoder that chose different match/literal
   splits than the original game's encoder for untouched bytes — valid
   per our decompressor, but not bit-identical to the original, and the
   PSX's real decompressor was sensitive to that difference. Fixed by
   porting Haruhiko Okumura's exact binary-tree LZSS (same algorithm
   ff7tk/qt-lzs/Makou Reactor use). Verified all 714 real LZS fields on
   the pristine disc recompress bit-identical to the original.
2. **BLACKBGB splice (workaround, not root-caused)**: even after the LZS
   fix, our own re-encode of BLACKBGB's DSKCG-stripped script still hung.
   Rather than keep chasing encoder parity for this one field, we now
   splice the user's own known-working compressed `FIELD/BLACKBGB.DAT`
   (manually edited + confirmed working in Makou Reactor) directly into
   the build, bypassing our re-encoder for this field entirely — via
   `build_work_bin.py --blackbgb-manual-bin` (accepts either a full
   working `.bin` or a raw extracted `.DAT` from
   `extract_field_from_bin.py`).

## How we found it

- Root cause: diffed our encoder's compressed bitstream against the
  original per-field, found match choices differed despite both being
  valid per the LZSS spec.
- BLACKBGB splice: since the true root cause (why our Okumura port still
  doesn't reproduce a working BLACKBGB after DSKCG removal) remains
  unexplained, the splice was adopted as a working, tested bypass.
- Verified via DuckStation emulator playtest: D1→D2 transition showed the
  "want to save?" prompt correctly, and LOST2's background rendered without
  corruption. Not yet tested on real PSX hardware.

## Why it matters

Unblocks the `single-disc-on-csr` release — both showstopper regressions
are resolved. The LZS encoder fix benefits every field in the pipeline;
the BLACKBGB splice is field-specific and should be revisited if we ever
figure out why our re-encoded version still hangs despite script-level
byte parity.

## Follow-ups

- [ ] Investigate why the Okumura-encoded BLACKBGB still hangs post-DSKCG-
      removal despite matching the manual edit's script bytes exactly —
      would let us drop the manual-splice dependency.
- [x] Confirm D1→D2 transition on DuckStation.
- [x] Confirm LOST2 background on DuckStation.
- [ ] Confirm both on real PSX hardware.

## Sources

- `scripts/lzs.py` (Okumura LZSS port)
- `mods/single-disc/scripts/build_work_bin.py` (`apply_manual_blackbgb`)
- `mods/single-disc/scripts/extract_field_from_bin.py`
- commits `924eba1`, `bd344d9`, `d713ded`
