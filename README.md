# Final Fantasy VII PSX Modding

Tools and notes for modifying **Final Fantasy VII** PlayStation disc images (hardware-compatible).

**Play:** https://individualcontributor.dev/builder/  
**Repo:** https://github.com/individualcontributordev/Final-Fantasy-7-Modding

## Mods

| Mod | Path | Builder | Changelog |
|-----|------|---------|-----------|
| Field random encounters | [mods/field-random-encounters/](mods/field-random-encounters/) | Light / Standard / Dense | [CHANGELOG](mods/field-random-encounters/CHANGELOG.md) |
| World map random encounters | [mods/world-map-random-encounters/](mods/world-map-random-encounters/) | Light / Standard / Dense | [CHANGELOG](mods/world-map-random-encounters/CHANGELOG.md) |
| Fanfare Skip | [mods/fanfare-skip/](mods/fanfare-skip/) | No victory song/poses (train-style) | [CHANGELOG](mods/fanfare-skip/CHANGELOG.md) |

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

## For engineers (RE) — build and mod this without an agent

**Start here:** [docs/00-goals.md](docs/00-goals.md) — the reading-order index for every doc below.
For a fully sequenced, exercise-based path from zero to shipping a mod, use
[docs/09-engineer-curriculum.md](docs/09-engineer-curriculum.md).

| Doc | Contents |
|-----|----------|
| [docs/03-environment-setup.md](docs/03-environment-setup.md) | Install checklist: emulator, Ghidra, Makou Reactor, hex tool |
| [docs/08-engineer-build-guide.md](docs/08-engineer-build-guide.md) | Build/verify disc images with only the CLI scripts (no agent needed) |
| [docs/02-disc-format.md](docs/02-disc-format.md) | ISO layout, GZIPPS compression, Makou save flow |
| [docs/04-workflow.md](docs/04-workflow.md) | Edit → recompress → reinsert → test loop |
| [docs/05-ghidra-guide.md](docs/05-ghidra-guide.md) | Ghidra import settings and RE method |
| [docs/01-encounter-system.md](docs/01-encounter-system.md) | Worked example: the field encounter RNG/RAM map |
| [docs/06-new-mod-research.md](docs/06-new-mod-research.md) | Idea → RE → patch → builder pack, end to end |
| [docs/07-hardware-burn.md](docs/07-hardware-burn.md) | MiSTer / PS2 burn verification ladder |
| [docs/reference/INDEX.md](docs/reference/INDEX.md) | Canonical field/movie/music ID tables and format references |
| [scripts/README.md](scripts/README.md) | Every shared CLI tool, what it's for, and quick-start commands |

After clone: `git config core.hooksPath .githooks`

## Suggestions backlog

Community-prioritised encounter/engine mods: [docs/SUGGESTIONS.md](docs/SUGGESTIONS.md)
## History

Story of CSR and mods (with archived chats):
[https://individualcontributor.dev/history/](https://individualcontributor.dev/history/)
