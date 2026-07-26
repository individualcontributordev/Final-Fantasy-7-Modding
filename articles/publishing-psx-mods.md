---
title: Publishing Final Fantasy VII PlayStation mods
date: 2026-07-26
summary: How mods on this site go from a pristine disc image to a single PPF and a browser patcher.
order: 1
---

# Publishing Final Fantasy VII PlayStation mods

Mods here target NTSC-U PlayStation disc images. Players apply one `.ppf` in the browser. Authors build that patch once against a pristine dump.

## Shipped checklist

1. **Pristine baseline** — retail `.bin` + `.cue`. PPF does not stack.
2. **Final image** — all edits applied (Makou field data, `FIELD.BIN` stubs, etc.).
3. **One `.ppf` per disc** — `scripts/make_ppf.py`, RomPatcher.js-compatible, verified on a second retail `.bin`.
4. **Site** — hub entry, patcher page (or shared scaffold), and an article in `articles/`.

Players do not need Makou, CDmage, or Ghidra.

## Author pipeline

```
retail .bin
  → optional Makou edits → Save ISO
  → extract changed engine file (often FIELD/FIELD.BIN)
  → decompress GZIPPS → patch → recompress
  → reimport into the same working image
  → DuckStation smoke test
  → make_ppf.py (pristine vs final)
  → site/<mod>/patches/ + PATCHES entry
  → articles/ post + hub link
```

### Makou vs engine code

Makou edits per-map `.DAT` (scripts, walkmesh, encounter tables). Encounter engine logic lives in compressed `FIELD/FIELD.BIN`.

If a release needs both:

1. Finish Makou → Save ISO.
2. Extract `FIELD/FIELD.BIN` from **that** image (not an earlier stock extract).
3. Patch and recompress.
4. Import over `FIELD/FIELD.BIN` on the same image.

Do not import a stock-based `FIELD.BIN.new` onto a Makou disc if sizes diverge. CDmage truncate → Cancel and restore. Shorter imports may pad with zeros.

### GZIPPS

`FIELD.BIN` is an 8-byte GZIPPS header plus gzip payload. Decompress to edit; recompress with project scripts and keep the header. Prefer patches that do not grow past the allocated size.

### PPF

```bash
python scripts/make_ppf.py \
  path/to/ff7_disc1_pristine.bin \
  path/to/ff7_disc1_final.bin \
  -o site/your-mod/patches/yourmod-disc1-v0.1.0.ppf \
  -d "Short public description" \
  --verify
```

Wire the file in the patcher’s `PATCHES` list (see `site/encounter/patches/README.md`).

## Private vs public

`docs/` and `docs/findings/` are internal notes. The site builds only from `articles/`.

## Next mod

| Step | Done when |
|------|-----------|
| Goal | One clear player-facing sentence |
| Layer | `.DAT`, engine, or Makou + engine (correct extract order) |
| Patch | Offsets/bytes or a script under `scripts/` + `workspace/patches/` |
| Test | Boot, relevant path, at least one fight; RAM checks if RNG-sensitive |
| PPF | From pristine; reapplied to a second retail image |
| Site | Hub, patcher entry, `articles/` post with `order` |
| Naming | **Final Fantasy VII** in player-facing copy |
