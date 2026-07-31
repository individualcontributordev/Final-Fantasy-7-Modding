# Final Fantasy VII PSX Modding

Tools and notes for modifying **Final Fantasy VII** PlayStation disc images (hardware-compatible).

**Play:** https://individualcontributor.dev/builder/  
**Repo:** https://github.com/individualcontributordev/Final-Fantasy-7-Modding

## Mods

| Mod | Path | Builder | Changelog |
|-----|------|---------|-----------|
| Field random encounters | [mods/field-random-encounters/](mods/field-random-encounters/) | Light / Standard / Dense | [CHANGELOG](mods/field-random-encounters/CHANGELOG.md) |
| World map random encounters | [mods/world-map-random-encounters/](mods/world-map-random-encounters/) | Light / Standard / Dense | [CHANGELOG](mods/world-map-random-encounters/CHANGELOG.md) |

Release notes index: **[CHANGELOGS.md](CHANGELOGS.md)** (newest entry at the **top** of each file).

## Layout

```
mods/<name>/          source of truth (VERSION, CHANGELOG, patches, scripts/)
mods/<name>/scripts/  that mod's build pipeline (build_all_rates, build_on_base, …)
builder/              published ic-layer-v1 packs + manifest.json (Pages CDN)
scripts/              shared only: ISO / gzip / layer / verify helpers
docs/                 RE reference + findings lab notebook
workspace/            local pristine discs / temps (gitignored)
CHANGELOGS.md         index of mod release notes (newest-at-top rule)
```

Mod build entrypoints live under `mods/<name>/scripts/`, not root `scripts/`.
Root `scripts/` is for reusable disc/ISO tools (`apply_layer`, `verify_*`, compress, …).

## Play

Use the disc builder: pick a cutscene base, optional Field encounter density, download zip.

## Release Field encounters

Needs `workspace/pristine/FINALFANTASY7_D1.bin` (never open in CDmage).

```bash
cd /c/path/to/Final-Fantasy-7-Modding
git pull

# bump mods/field-random-encounters/VERSION when shipping a new release
python mods/field-random-encounters/scripts/build_all_rates.py

git add builder/
git status   # JSON only — no .bin
git commit -m "Field encounters v0.1.2 — Light/Standard/Dense for clean + CSR bases."
git push
```

One pack (omit `--density` to pick Light / Standard / Dense / All interactively):

```bash
python mods/field-random-encounters/scripts/build_on_base.py --against csr --discs 1
# or non-interactive:
python mods/field-random-encounters/scripts/build_on_base.py --against csr --density light --discs 1
```

`--against` resolves the live CSR base id from Pages. Older packs stay enabled until you set `"enabled": false` in `builder/manifest.json`.

Densities are **named presets** (not a free-form %): **Light** / **Standard** / **Dense**. Stub notes: `mods/field-random-encounters/patches/`.

## For engineers (RE)

| Doc | Contents |
|-----|----------|
| [docs/06-new-mod-research.md](docs/06-new-mod-research.md) | Idea → RE → patch → builder pack |
| [docs/01-encounter-system.md](docs/01-encounter-system.md) | Field encounter RAM / Ghidra map |
| [docs/02-disc-format.md](docs/02-disc-format.md) | ISO, GZIPPS, Makou |
| [docs/03-environment-setup.md](docs/03-environment-setup.md) | Tools checklist |
| [docs/04-workflow.md](docs/04-workflow.md) | Edit → inject → verify |
| [docs/05-ghidra-guide.md](docs/05-ghidra-guide.md) | Ghidra workflow |
| [docs/findings/](docs/findings/) | Dated lab notebook |

After clone: `git config core.hooksPath .githooks`
