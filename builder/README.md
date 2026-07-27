# Builder packs (Pages publish surface)

JSON under this folder is what https://individualcontributor.dev/builder/ loads via
`remoteSources` → this repo’s Pages `/builder/manifest.json`.

Mod **source** lives under `mods/<name>/`. Builds write packs here.

```bash
python mods/field-random-encounters/scripts/build_all_rates.py
git add builder/
git commit -m "Field encounters vX.Y.Z — Light/Standard/Dense for clean + CSR bases."
git push
```

See `WINDOWS-INSTRUCTIONS.md`.
