# Final Fantasy VII PSX add-on layers

Stackable `ic-layer-v1` mods for the
[disc builder](https://individualcontributor.dev/builder/). Each mod targets one
exclusive base; the CSR, CSR+, and Highwind bases live in the CSR repo.

Published mods: field encounters, world encounters, fanfare skip. Field and
world encounters are chosen independently. `Unmodified` applies no mod and
keeps the game's own rate, which ramps between fights off a step counter and so
can be routed. The patches — `No Encs`, `Half Enc Rate`, `Vanilla Enc Rate`,
`Double Enc Rate` — replace that ramp with a flat roll off the RCnt2 timer,
which no route can predict.

Those labels are frequencies relative to the unmodified game, not a scale
applied to any byte: a flat roll cannot reproduce a ramp, so the thresholds are
calibrated while running, and walking fields come out somewhat busier than the
label promises. `Vanilla Enc Rate` is the unroutable equivalent of no mod at
all.

## Setup

Python 3.10+, all commands from the repo root. Retail NTSC-U MODE2/2352 images
go at `workspace/pristine/FINALFANTASY7_D{1,2,3}.bin` and are never edited.
Working BINs stay in `cache/<mod-id>/`; published metadata and layers in
`builder/`.

```bash
pip install zopfli
export FF7_CSR_ROOT=/path/to/Final-Fantasy-7-CSR

BASE=csr-plus                    # clean, csr, csr-plus, or highwind
MOD=fanfare-skip-on-csr-plus     # folder under builder/ and cache/
DISCS=(1)                        # csr and clean are (1 2 3); csr-plus and highwind are Disc 1 only
VERSION=X.Y.Z
```

Zopfli is the only dependency, and it is required: a recut overlay must fit the
ISO slot it came from, and stdlib `zlib` can miss that by a few bytes. On
Windows run `python`, not `python3` — that one is the Store shim.

`build_base_layer.py` infers the mod id from the BIN's parent folder
(`cache/<mod-id>/FINALFANTASY7_DN.bin`) and diffs against that pack's
`compatibleBases` entry, not against pristine.

## Build, edit, repair, publish

A new pack needs a stub `pack.json` first. `build_base_layer.py` will not
invent a mod from a BIN alone. Put this at `builder/$MOD/pack.json` (id must
match the folder) and leave `discs` / `discDigests` out — publish fills them:

```json
{
  "id": "fanfare-skip-on-csr-plus",
  "name": "Fanfare Skip",
  "kind": "mod",
  "blurb": "After the last enemy dies, skip the victory ceremony.",
  "hint": "No victory fanfare or win poses -- loot and exp still apply.",
  "format": "ic-layer-v1",
  "compatibleBases": ["csr-plus"]
}
```

One pack, one exclusive base. A Highwind cut is a different id
(`…-on-highwind`), not a second entry in `compatibleBases`.

Materialize the parent base, then start the mod BIN from it:

```bash
mkdir -p "cache/$BASE" "cache/$MOD"
for disc in "${DISCS[@]}"; do
  python3 scripts/apply_layer.py \
    "workspace/pristine/FINALFANTASY7_D${disc}.bin" \
    "$FF7_CSR_ROOT/builder/$BASE/layers/disc${disc}.layer.json" \
    -o "cache/$BASE/FINALFANTASY7_D${disc}.bin"
  cp "cache/$BASE/FINALFANTASY7_D${disc}.bin" "cache/$MOD/FINALFANTASY7_D${disc}.bin"
done
```

On `clean` there is no base layer: copy pristine instead. To edit an existing
pack, replace the `cp` with the same `apply_layer.py` call against
`builder/$MOD/layers/disc${disc}.layer.json`.

### Edit

These mods are MIPS stubs and data bytes: read the site in **Ghidra**, write it
with **ImHex**. Makou Reactor edits field scripts and belongs to the CSR repo,
not here.

The code is inside GZIPPS overlays (`FIELD/FIELD.BIN`, `WORLD/WORLD.BIN`,
`BATTLE/BATRES.X`), so a hex editor aimed at the disc image sees only
compressed bytes. Unwrap, patch the `.dec`, then rewrap into the same ISO slot:

```bash
python3 scripts/decompress_gzipps.py work/BATRES.X work/BATRES.X.dec
# Ghidra to locate, ImHex to edit work/BATRES.X.dec
python3 scripts/compress_gzipps.py work/BATRES.X.dec work/BATRES.X work/BATRES.X.new
```

Extract and pad-inject with `extract_file` / `replace_file_padded` from
`scripts/psx_mode2_iso.py`, which keeps the file's LBA. The per-mod scripts in
`mods/<name>/scripts/` run this end to end and are the working reference. A
same-length stub is a straight swap; anything that moves code needs its JAL
targets rechecked in Ghidra.

### Repair and publish

```bash
for disc in "${DISCS[@]}"; do
  image="cache/$MOD/FINALFANTASY7_D${disc}.bin"
  test -e "$image.bak" || cp "$image" "$image.bak"

  python3 scripts/repair_mode2_edc.py \
    "workspace/pristine/FINALFANTASY7_D${disc}.bin" "$image" -o "$image" || break

  python3 scripts/build_base_layer.py "$image" --version "$VERSION" || break

  python3 scripts/verify_builder_config.py \
    --disc "$disc" --base "$BASE" --addon "$MOD" --no-cache || break
done
```

Keep the `|| break`. Without it a failed publish is followed by a verify of the
*previously* published layer, which prints `PASS` and hides the failure.

Outputs are `builder/<mod>/layers/discN.layer.json`, `pack.json`, `VERSION`,
and `builder/manifest.json`. CSR+ and Highwind Disc 1 images are longer than
retail; repair uses pristine Disc 1 for overlapping sectors and recomputes
Form 1 footers on appended sectors.

## Rebuild overlay mods

Field encounters, world encounters, and fanfare skip are overlay recipes under
`mods/`, not hand-edited BINs. When the recipe or a parent base changes, recut
every pack from those scripts instead of the loop above:

```bash
python3 scripts/rebuild_on_base.py all  # every base, clean included
python3 scripts/rebuild_on_base.py csr  # one base
```

`all` always includes `clean`; a complete rebuild should not silently leave one
published base untouched. Recuts stamp `baseVersion` and leave `builder/` dirty
for you to review and commit.

Recuts run one at a time and the first failure stops the run, because a
half-recut pack keeps its old pin and would quietly disappear from the builder.
Zopfli and the LF rule are checked before any disc image is copied, so a
misconfigured clone fails in seconds instead of after a long build. Verify is a
separate command — do not recut just to check a pack.

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
python3 scripts/verify_builder_config.py all       # every base, clean included
python3 scripts/verify_builder_config.py csr-plus
python3 scripts/verify_builder_config.py \
  --disc 1 --base csr --addon fanfare-skip-on-csr --no-cache
```

The named bases walk every published addon compatible with that base, one mod
at a time, on each disc the base actually has. Fails on a stale pin or a layer
that does not apply cleanly. Not a substitute for DuckStation/MiSTer or a
console playtest.

Reconstructed bases are kept in `cache/<base>/` next to a `.version` sidecar
naming the CSR build they came from, and are rebuilt from pristine whenever CSR
publishes a new version. `--no-cache` forces that rebuild.

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
| `apply_layer.py IMAGE LAYER [-o OUT\|--expect BIN]`          | Apply or byte-verify an `ic-layer-v1` disc patch.                    |
| `decompress_gzipps.py OVERLAY [OUT.dec]`                    | Unwrap a GZIPPS overlay so Ghidra/ImHex see real code.               |
| `compress_gzipps.py OUT.dec ORIGINAL [OUT.new]`             | Rewrap a patched overlay, keeping it inside its ISO slot.            |
| `build_base_layer.py IMAGE --version X.Y.Z`                 | Publish one mod disc layer and merge pack.json / manifest metadata.  |
| `repair_mode2_edc.py PRISTINE IMAGE -o OUT`                 | Restore or recompute MODE2 Form 1 footers after editing.             |
| `verify_iso_integrity.py IMAGE`                             | Report duplicate LBAs, extent overlaps, and PVD size drift.          |
| `rebuild_on_base.py all\|clean\|csr\|csr-plus\|highwind`    | Recut overlay mods against the selected bases.                       |
| `verify_builder_config.py all\|clean\|csr\|csr-plus\|highwind` | Reconstruct and validate every mod on those bases.                 |
| `verify_builder_config.py --disc N --base ID [--addon ID]`  | Reconstruct and validate one builder stack.                          |
| `validate_manifest.py [PATH]`                               | Check ids, layer paths, published checksums, and LF line endings.    |

Shared code lives in `scripts/libs/`; per-mod overlay patchers
(`FIELD.BIN` / `WORLD.BIN` / `BATRES.X`) in `mods/<name>/scripts/`.
`psx_mode2_iso.py` is imported, not run: it extracts and pad-injects ISO9660
files without moving an LBA.

Commit as `individualcontributordev <contributorindividual@gmail.com>`.

## Archive

Retired scripts, docs, and mod data are indexed in [`ARCHIVE.md`](ARCHIVE.md)
with the commit that removed each one.
