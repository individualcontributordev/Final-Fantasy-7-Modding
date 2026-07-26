# Encounter patches

Drop RomPatcher-compatible `.ppf` files here, then wire them in [`../index.html`](../index.html).

## Example

1. Build a Disc 1 PPF (pristine NTSC-U `.bin` → patched image) via `scripts/make_ppf.py` in the repo root.
2. Copy it here as a short name, e.g. `encounter-disc1-v0.1.0.ppf`.
3. In `../index.html`, uncomment / add a `PATCHES` entry:

```js
{
  file: './patches/encounter-disc1-v0.1.0.ppf',
  name: 'Encounter — Disc 1 (v0.1.0)',
  description: 'RCnt2 FORCE stub — random-feeling field encounters. NTSC-U Disc 1 .bin',
  outputName: 'Final Fantasy VII (Disc 1) Encounter v0.1.0'
}
```

4. Commit and push — GitHub Pages redeploys from `main`.

See also `docs/06-packaging-combined-ppf.md` for Makou + stub packaging.
