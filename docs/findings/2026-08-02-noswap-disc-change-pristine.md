# No-disc-swap RE — pristine D1 disc identity + field disc-change

**Date:** 2026-08-02
**Confidence:** confirmed (ISO dump + Makou script paste)
**Sources:** `docs/INSTRUCTIONS.md` evidence (commit 2cc2a11); pristine D1 working copy

## Goal

How Unmodified Disc 1 encodes disc id and requests other discs. Baseline for an any-base no-disc-swap add-on.

## ISO / files (D1)

| Path | Notes |
|------|--------|
| `SYSTEM.CNF` | Boots `SCUS_941.63` |
| `MINT/DISKINFO.CNF` | Starts with `DISK0001` (disc label file) |
| `MINT/MOVIE_ID.BIN` | 1080 bytes — per-disc movie index |
| `MOVIE/DISK1.LZS` / `DISK2.LZS` / `DISK3.LZS` | ~28 KB each — likely disc-change UI graphics |

Whole-image strings on D1:

- `DISK0001`: 1 hit (inside `DISKINFO.CNF` payload)
- `DISK0002` / `DISK0003`: **0** hits on the D1 image (other disc labels not stored on D1)
- English `Please insert` / `insert disc`: **0** hits — prompt is not plain ASCII English on the disc image
- `DISKINFO`: 2 hits (directory name + path)

## Field scripts (Makou) — primary swap mechanism

Disc changes are **field script opcodes**, not only a boot file check. Example group paste (blackbg / related flow) shows:

1. Optional save prompt; set `Var[13][0]` to target disc number (`2` or `3`)
2. **`Ask for disc 2`** or **`Ask for disc 3`**
3. Wait / music
4. **`Jump to map`** on the other disc (e.g. `lost2` #634 after disc 2; `las0_1` #744 after disc 3)

Also present: multi-disc movie pick, e.g.  
`Set next movie: rcktfail (disc 1), rckethit1 (disc 2), No45 (disc 3)` then `Play movie`.

So a no-disc-swap pack must at least:

1. Neutralize or no-op **Ask for disc N** (or always succeed with current medium)
2. Keep the following **map jump** on the same physical image (maps must exist on that image — full FIELD set is shared across retail discs)
3. Handle **disc-qualified movies** (skip / pick existing STR / stub)
4. Optionally spoof **`MINT/DISKINFO.CNF`** if anything re-reads disc id after boot

## Implications for any-base mod

- Primary work is **FIELD `.DAT` script edits** (and maybe movie table / `DISKINFO`), against **pristine** first; then verify identical bytes on CSR / Highwind or ship per-base packs.
- CSR/Highwind already edit some maps — list every `Ask for disc` map before assuming one layer fits all bases.

## Next RE

Full Makou **Find All** for `Ask for disc` (and movie disc triplets) on pristine D1; table of map + script + target disc + following jump.
