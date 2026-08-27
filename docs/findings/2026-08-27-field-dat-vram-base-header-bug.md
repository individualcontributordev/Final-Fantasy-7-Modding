# FIELD/*.DAT rewrite used hardcoded VRAM base, corrupting 6 precision-patched fields

**Date:** 2026-08-27
**Confidence:** confirmed
**Status:** promoted (fixed in `adb07fc`)
**Related:** `docs/findings/2026-08-26-junair-single-disc-battle-return-freeze.md` (this was
investigated as a possible cause of that freeze; ruled out as the same bug since the
freeze reproduces on stock CSR D2 alone — but this bug was real and independently fixed)

## Summary

`write_field_dat()` recomputed every FIELD/*.DAT's 28-byte VRAM section-pointer
header using a hardcoded `0x80000000` base instead of the field's own load
address (`fd.vbase`), corrupting internal pointers on every precision-patched
field. The file still "loaded" (passed basic checks) but crashed/froze at
runtime when the engine dereferenced the wrong section pointers.

## Context

Debugging a black-screen hang on JUNAIR (field 384) return-from-battle. Static
diffing showed the field content itself was untouched, but the *rebuilt*
(precision-patched) `.DAT` behaved differently from a byte-identical original.

## Field DAT format reference (for future readers — not previously documented in this repo)

Confirmed against public wikis (ffrtt.ru, ff7-flat-wiki, PyFF7, ff7tools) — this
part of the format is well known community-wide, just not written down here yet:

- Compressed `.DAT` on disc: 4-byte LE length + LZSS-compressed payload.
- Decompressed `.DAT` starts with a **28-byte header**: 7 little-endian
  4-byte **absolute PS1 RAM addresses** (not file offsets), one per section
  (scripts, camera, background/walkmesh, model loader, palette, encounter,
  inf, etc. — order project-specific).
- Each pointer = `vbase + running_offset_from_byte_28`, where `vbase` is
  **the field's own load address** — this differs per field (e.g. JUNAIR
  loads at `0x80115000`, not `0x80000000`). Section length is derived by
  subtracting adjacent pointers.
- Sources: https://wiki.ffrtt.ru/index.php/FF7/Field_Module,
  https://wiki.ffrtt.ru/index.php/FF7/Field,
  https://ff7-mods.github.io/ff7-flat-wiki/FF7/Field.html,
  https://github.com/niemasd/PyFF7/blob/master/PyFF7/field.py,
  https://deepwiki.com/cebix/ff7tools/3.1-field-map-parser-(ff7.field)

## Discovery

`scripts/field_dat.py`'s **read** path (`load_field_dat`) already extracted
`vbase` correctly per file. `scripts/field_dat_write.py`'s **write** path
recomputed the header using a hardcoded `0x80000000` constant instead of
reusing `fd.vbase`:

```python
# Before (bug): hardcoded base
offs.append(0x80000000 + cur_pos)

# After (fix): use the field's own load address
vbase = fd.vbase
offs.append(vbase + cur_pos)
```

Fields with `vbase == 0x80000000` were unaffected by coincidence. Fields
loading elsewhere (JUNAIR `0x80115000`, WHITE2, BUGIN1A, NIVGATE, RCKTIN2,
and the BLACKBGB DSKCG-removal splice) got a header full of wrong absolute
addresses — the engine read/wrote through those bad pointers, causing a
black-screen hard freeze instead of a clean failure, since the file still
passed the loader's basic length/section-count checks.

## How we found it

Not from any online reference — the format itself was already correctly
understood in this repo's own read path. Found by tracing the header-rebuild
math in `field_dat_write.py`, noticing it used a literal constant, and
confirming `load_field_dat` already had the right per-field value available
(`fd.vbase`) that the write path simply failed to reuse. Verified fix by
diffing rebuilt JUNAIR.DAT against byte-identical CSR D2 original.

## Why it matters

Any tool in this repo that rewrites a `FIELD/*.DAT` (precision patcher,
splicers, mergers) must pull `vbase` from the parsed source field, never
assume a constant. This is a generic correctness requirement for
`write_field_dat()`, not a JUNAIR-specific patch. Affected 6 fields in one
release; likely to recur if a new call site reintroduces a hardcoded base.

## Related VRAM/texture-cache research (background for cosmetic glitches)

Separately researched while investigating the JUNAIR elevator "missing
squares" cosmetic glitch (still open, not caused by this bug — reproduces on
an external known-good reference build too):

- PSX VRAM is a 1024x512 (or 2048x512 depending on source) pixel "surface".
  Field textures live in a **"transient texture cache"** region that is the
  *first* area overwritten when another module (e.g. Battle) loads. A
  "semi-permanent" area below it tends to persist across module loads.
  Source: https://forums.qhimm.com/index.php?topic=480.0 (Halkun,
  "Field Files/Texture management"),
  https://wiki.ffrtt.ru/index.php/FF7/Kernel/Memory_management
- Background layers are rendered from 16x16 tile blocks re-assembled into
  the video buffer every frame; `BGON`/`BGOFF`/`BGSCR` opcodes toggle/scroll
  pre-loaded layer IDs — they do not re-upload texture data themselves.
  Source: https://wiki.ffrtt.ru/index.php/FF7/Field/Script/Opcodes/E0_BGON
- Working hypothesis for the elevator glitch: returning from Battle
  overwrites the transient texture cache region the elevator's background
  layers depend on, and the field-reinit path doesn't reissue the upload for
  those specific layers — consistent with "static frame, squares missing"
  rather than flicker/garbage. **Not yet confirmed with a live VRAM viewer**
  (see the open item in the JUNAIR freeze finding for that dependency).

## Follow-ups

- [x] Fix `write_field_dat()` to use `fd.vbase` (done, `adb07fc`).
- [ ] Confirm elevator glitch mechanism with DuckStation VRAM viewer during
      the `BGON e0000300`/`e0000500` sequence on battle-return.
- [ ] Audit for any other call site that rebuilds a field DAT header with a
      literal base instead of `vbase`.

## Sources

- https://wiki.ffrtt.ru/index.php/FF7/Field_Module
- https://wiki.ffrtt.ru/index.php/FF7/Field
- https://ff7-mods.github.io/ff7-flat-wiki/FF7/Field.html
- https://github.com/niemasd/PyFF7/blob/master/PyFF7/field.py
- https://deepwiki.com/cebix/ff7tools/3.1-field-map-parser-(ff7.field)
- https://forums.qhimm.com/index.php?topic=480.0
- https://wiki.ffrtt.ru/index.php/FF7/Kernel/Memory_management
- https://wiki.ffrtt.ru/index.php/FF7/Field/Script/Opcodes/E0_BGON
- Repo: `scripts/field_dat.py`, `scripts/field_dat_write.py`, commit `adb07fc`
