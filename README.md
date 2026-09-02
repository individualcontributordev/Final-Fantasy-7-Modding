# Final Fantasy VII PSX add-on layers

This repository publishes stackable `ic-layer-v1` mods for the
[disc builder](https://individualcontributor.dev/builder/). CSR, CSR+, and
Highwind bases live in the separate CSR checkout. Mods here are mutually
compatible with one exclusive base each.

All commands run from this repository's root and require Python 3.10 or newer.
The command names and flags match the CSR repo.

Place clean NTSC-U raw MODE2/2352 images at:

```text
workspace/pristine/FINALFANTASY7_D1.bin
workspace/pristine/FINALFANTASY7_D2.bin
workspace/pristine/FINALFANTASY7_D3.bin
```

Never edit `workspace/pristine/`. Working BINs stay under `cache/<mod-id>/`;
published metadata and layers are under `builder/`. CSR bases are read through
`--csr-root` or:

```bash
export FF7_CSR_ROOT=/path/to/Final-Fantasy-7-CSR
```

## Apply, edit, repair, publish

Every mod uses the same loop as a CSR base: apply the published layer onto
its parent BIN, edit, repair Form 1 footers, then publish a replacement layer.

Choose the mod and its discs. The parent is the exclusive base that mod
lists in `compatibleBases` (clean, csr, csr-plus, or highwind).

```bash
MOD=fanfare-skip-on-csr-plus
BASE=csr-plus
DISCS=(1)
VERSION=0.1.7
```

Materialize the parent base, then the mod:

```bash
mkdir -p "cache/$BASE" "cache/$MOD"
for disc in "${DISCS[@]}"; do
  python3 scripts/apply_layer.py \
    "workspace/pristine/FINALFANTASY7_D${disc}.bin" \
    "$FF7_CSR_ROOT/builder/$BASE/layers/disc${disc}.layer.json" \
    -o "cache/$BASE/FINALFANTASY7_D${disc}.bin"

  python3 scripts/apply_layer.py \
    "cache/$BASE/FINALFANTASY7_D${disc}.bin" \
    "builder/$MOD/layers/disc${disc}.layer.json" \
    -o "cache/$MOD/FINALFANTASY7_D${disc}.bin"
done
```

For a clean-base mod such as `fanfare-skip`, skip the CSR apply and use
`workspace/pristine/FINALFANTASY7_DN.bin` as the first `apply_layer` image.

If the CSR+ BIN already exists, point `--parent` or the first `apply_layer`
image at that file instead of reconstructing it.

Edit `cache/<mod-id>/FINALFANTASY7_DN.bin` in Makou Reactor. Repair and publish
every edited disc:

```bash
for disc in "${DISCS[@]}"; do
  image="cache/$MOD/FINALFANTASY7_D${disc}.bin"
  test -e "$image.bak" || cp "$image" "$image.bak"

  python3 scripts/repair_mode2_edc.py \
    "workspace/pristine/FINALFANTASY7_D${disc}.bin" \
    "$image" \
    -o "$image"

  python3 scripts/build_base_layer.py \
    "$image" \
    --version "$VERSION"

  python3 scripts/verify_builder_config.py \
    --disc "$disc" \
    --base "$BASE" \
    --addon "$MOD" \
    --no-cache
done
```

`build_base_layer.py` infers the mod from `cache/<mod-id>/` and diffs against
that mod's parent base, not against pristine. Outputs are
`builder/<mod-id>/layers/discN.layer.json`, `pack.json`, `VERSION`, and
`builder/manifest.json`.

## Verification

```bash
python3 scripts/apply_layer.py \
  "cache/$BASE/FINALFANTASY7_D${DISCS}.bin" \
  "builder/$MOD/layers/disc${DISCS}.layer.json" \
  --expect "cache/$MOD/FINALFANTASY7_D${DISCS}.bin"
```

Automated checks do not replace DuckStation/MiSTer testing or a console
playtest.

## Script reference

| Command                                                    | Purpose                                                                 |
| ---------------------------------------------------------- | ----------------------------------------------------------------------- |
| `apply_layer.py IMAGE LAYER [-o OUT\|--expect BIN]`         | Apply or byte-verify an `ic-layer-v1` disc patch.                       |
| `build_base_layer.py IMAGE --version X.Y.Z`                | Publish one mod disc layer and merge pack.json / manifest metadata.     |
| `repair_mode2_edc.py PRISTINE IMAGE -o OUT`                | Restore or recompute MODE2 Form 1 footers after editing.                |
| `verify_builder_config.py --disc N --base ID [--addon ID]` | Reconstruct and validate the selected builder stack.                    |

Shared implementation lives under `scripts/libs/`. Overlay authoring helpers
remain under `mods/<name>/scripts/` (FIELD.BIN / WORLD.BIN / BATTLE.X patches)
and are not required for the apply → edit → repair → publish loop.

The hosted builder reads:

```text
https://individualcontributor.dev/Final-Fantasy-7-Modding/builder/manifest.json
```
