# Final Fantasy VII PSX Modding

Tools and notes for modifying **Final Fantasy VII** PlayStation disc images (hardware-compatible).

**Play:** https://individualcontributor.dev/builder/  
**Repo:** https://github.com/individualcontributordev/Final-Fantasy-7-Modding

## Mods

| Mod | Path | Builder |
|-----|------|---------|
| Field random encounters | [mods/field-random-encounters/](mods/field-random-encounters/) | Light / Standard / Dense |
| World map random encounters | [mods/world-map-random-encounters/](mods/world-map-random-encounters/) | scaffold only |

## Layout

```
mods/          per-mod source (VERSION, patches, build scripts)
builder/       published ic-layer-v1 packs + manifest (Pages JSON CDN)
scripts/       shared ISO / gzip / layer helpers
docs/          guides + findings (engineers)
workspace/     local pristine discs / temps (gitignored binaries)
```

## Release (Field encounters)

1. Bump `mods/field-random-encounters/VERSION` if needed  
2. `workspace/pristine/FINALFANTASY7_D1.bin` present  
3. `python mods/field-random-encounters/scripts/build_all_rates.py`  
4. Commit `builder/` JSON only → push (Pages serves `/builder/`)

Details: [builder/WINDOWS-INSTRUCTIONS.md](builder/WINDOWS-INSTRUCTIONS.md)

## Docs for engineers

Start at [docs/00-goals.md](docs/00-goals.md). Encounter system: [docs/01-encounter-system.md](docs/01-encounter-system.md). Lab notebook: [docs/findings/](docs/findings/).

After clone: `git config core.hooksPath .githooks`
