---
title: Publishing Final Fantasy VII PlayStation mods
date: 2026-07-26
summary: How a Final Fantasy VII PlayStation mod becomes a single PPF you apply in the browser.
order: 1
---

# Publishing Final Fantasy VII PlayStation mods

These mods ship as **PPF** patches for NTSC-U PlayStation disc images (`.bin`). You apply them in the browser; nothing is uploaded. Each patch is built once against an untouched retail dump — PPF does not stack.

## What goes into a release

A finished disc mod is a pristine retail image with every intended change applied, then diffed into one `.ppf` per disc. Typical layers:

- **Field / map data** — per-map `.DAT` edits (scripts, walkmesh, encounter tables), often via Makou Reactor.
- **Engine code** — compressed binaries such as `FIELD/FIELD.BIN` (field logic) or later `WORLD.BIN`.

Players only need the `.ppf` and a clean `.bin`.

## Building the modified disc

```
retail .bin
  → optional Makou field edits → save ISO
  → extract the engine file that changed (often FIELD/FIELD.BIN)
  → decompress → patch bytes → recompress
  → reimport into the same working image
  → test in DuckStation
  → diff pristine vs final → .ppf
```

### Makou and FIELD.BIN

Makou edits map files. Encounter *engine* behavior (Danger growth, RNG calls) lives in compressed `FIELD/FIELD.BIN`. When both are needed: finish Makou and save the ISO first, then extract and patch `FIELD/FIELD.BIN` from **that** image, then reimport over the same path. Patching a stock extract and dropping it onto a Makou disc can break Square’s file index or truncate on import.

### GZIPPS

On disc, `FIELD.BIN` starts with an 8-byte GZIPPS header plus a gzip payload. The file is decompressed for editing, then recompressed with the header preserved. Imports that are slightly shorter than the original slot can pad; imports that would truncate should be rejected.

### The PPF

The release artifact is a RomPatcher.js-compatible PPF 3.0 file: pristine retail `.bin` versus the final modified image, with a short description string. Applying that PPF to a second clean retail image must match the final build before it goes on the patcher page.

## Related

- [Remaking field encounters](./remaking-field-encounters.html) — the first engine stub built this way
