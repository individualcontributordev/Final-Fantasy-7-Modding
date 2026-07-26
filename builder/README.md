# Builder packs (Modding)

Stackable `ic-layer-v1` packs for https://individualcontributor.dev/builder/

Do **not** commit `.bin` / `.cue` game images. Only JSON manifests + layer files.

## Pack layout

```
builder/
  manifest.json                 # listed on the main site via remoteSources
  encounter-v0.1.0/
    pack.json                   # metadata for this pack
    layers/
      disc1.layer.json          # produced on Windows — see WINDOWS-INSTRUCTIONS.md
```

## Windows

Follow [WINDOWS-INSTRUCTIONS.md](./WINDOWS-INSTRUCTIONS.md).
