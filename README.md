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
pip install zopfli
export FF7_CSR_ROOT=/path/to/Final-Fantasy-7-CSR
```

Zopfli is the only dependency, and it is required: a recut overlay must fit the
ISO slot it came from, and stdlib `zlib` can miss that by a few bytes. On
Windows run `python`, not `python3` — that one is the Store shim.

## Rebuild mods

```bash
python3 scripts/rebuild_on_base.py all    # csr + csr-plus + highwind
python3 scripts/rebuild_on_base.py csr    # one base
```

Recuts each mod against the current bases, stamps `baseVersion`, and leaves
`builder/` dirty for you to review and commit. Working BINs go to `cache/`.
Recuts run one at a time, and the first failure stops the run: a half-recut
pack keeps its old `baseVersion` and would quietly disappear from the builder.

Before copying any disc image it checks that zopfli is installed and that git
pins `builder/*.json` to LF, so a misconfigured clone fails in seconds instead
of after a long build.

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

```bash
python3 scripts/validate_manifest.py
```

Run this before pushing. The builder refuses any layer whose bytes do not hash
to the checksum published beside it, so a stale `discDigests` entry takes that
pack offline with no other warning. Failures print the fix for each problem.

Push `main`. GitHub Pages deploys `builder/` to
`https://individualcontributor.dev/Final-Fantasy-7-Modding/builder/`, which is
what the hosted builder reads. Commit JSON under `builder/` only — never
`.bin` or `.cue`.

Checksums cover the exact bytes git serves, so `builder/*.json` is pinned to LF
by `.gitattributes`. Building mods on a Mac and bases on Windows is fine;
publishing from a CRLF checkout is not.

## Script reference

| Command                                                     | Purpose                                                             |
| ----------------------------------------------------------- | -------------------------------------------------------------------- |
| `rebuild_on_base.py csr\|csr-plus\|highwind\|all`            | Recut every mod against the current CSR bases.                       |
| `apply_layer.py IMAGE LAYER [-o OUT\|--expect BIN]`          | Apply or byte-verify an `ic-layer-v1` disc patch.                    |
| `build_base_layer.py IMAGE --version X.Y.Z`                 | Publish one mod disc layer and merge pack.json / manifest metadata.  |
| `repair_mode2_edc.py PRISTINE IMAGE -o OUT`                 | Restore or recompute MODE2 Form 1 footers after editing.             |
| `verify_builder_config.py --disc N --base ID [--addon ID]`  | Reconstruct and validate the selected builder stack.                 |
| `validate_manifest.py [PATH]`                               | Check ids, layer paths, published checksums, and LF line endings.    |

Shared code lives in `scripts/libs/`; per-mod overlay patchers
(`FIELD.BIN` / `WORLD.BIN` / `BATRES.X`) in `mods/<name>/scripts/`.

Commit as `individualcontributordev <contributorindividual@gmail.com>`.
