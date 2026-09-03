# Final Fantasy VII PSX add-on layers

Stackable `ic-layer-v1` mods for the
[disc builder](https://individualcontributor.dev/builder/). Each mod targets one
exclusive base; the CSR, CSR+, and Highwind bases live in the CSR repo.

Published mods: field encounters, world encounters, fanfare skip. Encounter
density ships as four named rates (`off` / `light` / `standard` / `dense` →
0/25/50/75); field and world are chosen independently in the builder.

## Setup

Python 3.10+, all commands from the repo root. Retail NTSC-U MODE2/2352 images
go at `workspace/pristine/FINALFANTASY7_D{1,2,3}.bin` and are never edited.

```bash
python3 scripts/bootstrap_venv.py     # .venv + zopfli, once per clone
source .venv/bin/activate             # Windows: .venv\Scripts\activate
export FF7_CSR_ROOT=/path/to/Final-Fantasy-7-CSR
```

Use `python` after activating — on Windows `python3` still hits the Store shim.
Zopfli is required because a recut overlay must fit the ISO slot it came from,
and stdlib `zlib` can miss that by a few bytes.

## Rebuild mods

```bash
python scripts/rebuild_on_base.py all             # csr + csr-plus + highwind
python scripts/rebuild_on_base.py csr --jobs 1    # one base, sequential
```

Recuts each mod against the current bases, stamps `baseVersion`, and leaves
`builder/` dirty for you to review and commit. Working BINs go to `cache/`.
Families run in parallel (default `--jobs 3`, capped by RAM since each copies
disc images); a failure is reported at the end without cancelling the rest.

To publish a layer from a BIN you edited by hand, run `build_base_layer.py`
directly — it diffs against the mod's parent base, not pristine.

## Mods are pinned to one base build

A layer is `{offset, hex}` writes with no expected bytes, so applying it over a
base it was not cut from patches whatever now sits at those offsets and
silently corrupts the image. Each pack records the `baseVersion` it was cut
from, and the builder hides any mod whose pin is not the base's current
version.

**Bump a base, recut every mod on it.** Never hand-edit a pin onto an old
layer; the offsets still belong to the previous base. `clean` packs carry no
pin because pristine never changes.

## Verify

```bash
python scripts/verify_builder_config.py \
  --disc 1 --base csr --addon fanfare-skip-on-csr --no-cache
```

Fails on a stale pin or a layer that does not apply cleanly. Not a substitute
for DuckStation/MiSTer or a console playtest.

## Publish

Push `main`. GitHub Pages deploys `builder/` to
`https://individualcontributor.dev/Final-Fantasy-7-Modding/builder/`, which is
what the hosted builder reads. Commit JSON under `builder/` only — never
`.bin` or `.cue`.

## Script reference

| Command                                                     | Purpose                                                             |
| ----------------------------------------------------------- | -------------------------------------------------------------------- |
| `rebuild_on_base.py csr\|csr-plus\|highwind\|all [--jobs N]`  | Recut every mod against the current CSR bases.                       |
| `apply_layer.py IMAGE LAYER [-o OUT\|--expect BIN]`          | Apply or byte-verify an `ic-layer-v1` disc patch.                    |
| `build_base_layer.py IMAGE --version X.Y.Z`                 | Publish one mod disc layer and merge pack.json / manifest metadata.  |
| `repair_mode2_edc.py PRISTINE IMAGE -o OUT`                 | Restore or recompute MODE2 Form 1 footers after editing.             |
| `verify_builder_config.py --disc N --base ID [--addon ID]`  | Reconstruct and validate the selected builder stack.                 |
| `validate_manifest.py [PATH]`                               | Check add-on ids and on-disk layer paths.                            |
| `bootstrap_venv.py`                                         | Create `.venv` and install `requirements.txt`.                       |

Shared code lives in `scripts/libs/`; per-mod overlay patchers
(`FIELD.BIN` / `WORLD.BIN` / `BATRES.X`) in `mods/<name>/scripts/`.

Commit as `individualcontributordev <contributorindividual@gmail.com>`.
