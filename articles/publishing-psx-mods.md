---
title: Publishing Final Fantasy VII PlayStation mods
date: 2026-07-26
summary: How IndividualContributor turns engine research into a single PPF and a browser patcher — the template for every mod we ship next.
order: 1
---

# Publishing Final Fantasy VII PlayStation mods

Final Fantasy VII on PlayStation is not a folder of loose files you can zip up and hand to a friend. It is a Mode-2 disc image: custom indexes inside compressed engine blobs, per-map field data, and a save path that will happily truncate the wrong file if you blink. The mods on this site are built for that world — and for players who only want a `.bin`, a patch, and a download button.

This article is the publishing template. The [encounter rate work](./remaking-field-encounters.html) is the first deep dive that follows it. Future mods should land the same way: research in public prose, patches as RomPatcher-compatible PPFs, and a themed browser page that never uploads your disc.

## What “shipped” means here

A finished mod on IndividualContributor has four pieces:

1. **A pristine baseline** — NTSC-U retail disc images (`.bin` + `.cue`). Patches are always measured against an untouched dump. PPF does not stack; two half-finished patches do not become one finished one.
2. **A final disc image** — every change (Makou field edits, `FIELD.BIN` engine stubs, anything else) applied to that baseline until the game behaves the way you intend.
3. **One `.ppf` per disc** — built with `scripts/make_ppf.py` so [RomPatcher.js](https://github.com/marcrobledo/RomPatcher.js) and the on-site patchers can apply it. Description string included; verified by applying the PPF to a second fresh retail `.bin`.
4. **A public surface** — hub listing, optional dedicated patcher page under `site/`, and a research article in `articles/` that explains the *why* and *how* without dumping the lab notebook.

Players never need Makou, CDmage, Ghidra, or Python. Authors do — once — so everyone else can stay in the browser.

## The author pipeline (every engine-touching mod)

The loop is the same whether you are rewriting encounter Danger or something in `WORLD.BIN` later:

```
retail .bin
    → optional Makou field / map edits → Save ISO
    → extract the engine file you changed (often FIELD/FIELD.BIN)
    → decompress GZIPPS → patch decompressed bytes → recompress
    → reimport into the same working image
    → DuckStation smoke test (boot, field, fight, any RAM checks)
    → make_ppf.py (pristine vs final)
    → drop .ppf into site/<mod>/patches/ and wire PATCHES in the patcher page
    → write an articles/ post and link it from the hub
```

### Makou and engine code are different layers

Makou Reactor is excellent for per-map `.DAT` work (scripts, walkmesh, encounter *tables*). It does not rewrite the field engine’s Danger accumulation. That logic lives in compressed `FIELD/FIELD.BIN`.

When a mod needs both:

- Finish Makou edits and **Save ISO** first.
- Extract **`FIELD/FIELD.BIN` from that Makou-saved disc**, not from a stock dump you patched earlier.
- Run the stub (or other engine patch) through `scripts/build_field_encounter_patch.py` / the decompress → patch → compress scripts.
- Import `FIELD.BIN.new` back over **`FIELD/FIELD.BIN`** on the same image.

Never drop a stock-based `FIELD.BIN.new` onto a Makou disc if sizes or indexes diverge — you can wipe Square’s custom file index or hit CDmage’s truncate dialog. Truncate means **Cancel**, restore a pristine working copy, and start that step again. Shorter-than-slot imports may pad with zeros; that path is fine when you expected a slight shrink after recompress.

### GZIPPS in one paragraph

On disc, `FIELD.BIN` begins with an 8-byte GZIPPS header (decompressed size + a gzip sub-header you must preserve) and a gzip payload. Decompress to edit MIPS and tables; recompress with the project scripts so the header stays honest. Small in-place stubs often come out a few dozen bytes *smaller* than stock — good for reimport. Growth past the allocated space forces relocation and index updates; do not accept a truncated write.

### One PPF, then the browser page

```bash
python scripts/make_ppf.py \
  path/to/ff7_disc1_pristine.bin \
  path/to/ff7_disc1_final.bin \
  -o site/your-mod/patches/yourmod-disc1-v0.1.0.ppf \
  -d "Your mod — short public description" \
  --verify
```

Mirror the CSR pattern: each disc is its own patch entry, with a clear `outputName` for the downloaded `.bin` and an auto-matched `.cue`. Document the drop-in steps next to the patcher (see `site/encounter/patches/README.md` for the encounter scaffold).

## What stays private

`docs/` and `docs/findings/` are the working journal — addresses chased at 2 a.m., wrong `FIELD.BIN` targets, COP0 Count mistakes, RAM pokes. Useful for the next session; terrible as a homepage. The public research section only builds from `articles/`.

When a discovery earns a lasting explanation, fold it into a post. Leave the raw dated notes in the repo for authors.

## Checklist for the next mod

| Step | Done when |
|------|-----------|
| Goal written | One sentence a runner or casual player would care about |
| Layer chosen | `.DAT` only, engine only, or Makou + engine with correct extract order |
| Patch recorded | Offsets / VA, old→new bytes, or a scripted applicator in `scripts/` + `workspace/patches/` |
| Playtested | Boot, relevant field/world path, at least one fight; RAM checks if the claim is RNG-sensitive |
| Single PPF | Diffed from pristine; reapplied to a second retail image |
| Site | Hub blurb, patcher `PATCHES` entry (or new page), research article with `order` set |
| Naming | Prefer **Final Fantasy VII** in titles and player-facing copy |

That is the contract. The encounter article shows what it looks like when the contract is filled with real MIPS.
