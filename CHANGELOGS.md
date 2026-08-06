# Changelogs (Modding repo)

**Newest release at the top** of each file. Oldest at the bottom.

Builder pack ids live in `builder/manifest.json`. Notes go next to the mod source.

## Layout

| Product | Changelog | Live packs (see manifest) |
|---------|-----------|---------------------------|
| Field random encounters | [mods/field-random-encounters/CHANGELOG.md](mods/field-random-encounters/CHANGELOG.md) | `field-encounter-*-v…`, `field-encounter-on-*-v…` |
| World map random encounters | [mods/world-map-random-encounters/CHANGELOG.md](mods/world-map-random-encounters/CHANGELOG.md) | `world-encounter-*-v…`, `world-encounter-on-*-v…` |
| Single-disc | [mods/single-disc/CHANGELOG.md](mods/single-disc/CHANGELOG.md) | `single-disc-on-csr-v0.1.2`, manip-movies v0.1.0+v0.1.1 |
| Builder presets (this repo) | note under the mod(s) that own the packs | e.g. preset `random-encounters-light` |

```text
mods/<mod>/CHANGELOG.md   player-facing + pack version history
mods/<mod>/VERSION          current ship version (semver)
builder/<pack-id>/          layers only — no long prose
```

## Entry format

```markdown
## vX.Y.Z (YYYY-MM-DD)

- One line per player-visible or ship-visible change.
- Mention bases (clean / csr / highwind) and densities when relevant.
```

## Who updates

| Workflow | Skill | File |
|----------|-------|------|
| Ship field densities | `ship-field-encounters` | `mods/field-random-encounters/CHANGELOG.md` + `VERSION` |
| Ship world densities | `ship-world-encounters` | `mods/world-map-random-encounters/CHANGELOG.md` + `VERSION` |

Same git push as `builder/` for that release.
## Backlog

- Community suggestions (prioritised): [docs/SUGGESTIONS.md](docs/SUGGESTIONS.md)
## History

- [https://individualcontributor.dev/history/](https://individualcontributor.dev/history/)

## single-disc

See [mods/single-disc/CHANGELOG.md](mods/single-disc/CHANGELOG.md).
