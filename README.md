# Final Fantasy VII PSX add-on layers

Stackable `ic-layer-v1` mods for the
[disc builder](https://individualcontributor.dev/builder/). Each mod targets one
exclusive base; the CSR, CSR+, and Highwind bases live in the CSR repo.

Published mods: field encounters, world encounters, fanfare skip. Field and
world encounters are chosen independently: `Vanilla` applies no mod, while
`No Encs`, `Half Enc Rate`, and `Double Enc Rate` apply fixed patches. Double
saturates the game's one-byte encounter threshold instead of wrapping it.

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

Materialize the parent, then the currently published addon if you are editing
an existing pack. Skip the second `apply_layer` for a new mod — the parent BIN
is what you start from:

```bash
mkdir -p "cache/$BASE" "cache/$MOD"
for disc in "${DISCS[@]}"; do
  parent="workspace/pristine/FINALFANTASY7_D${disc}.bin"
  if [ "$BASE" != "clean" ]; then
    python3 scripts/apply_layer.py \
      "$parent" \
      "$FF7_CSR_ROOT/builder/$BASE/layers/disc${disc}.layer.json" \
      -o "cache/$BASE/FINALFANTASY7_D${disc}.bin"
    parent="cache/$BASE/FINALFANTASY7_D${disc}.bin"
  fi

  layer="builder/$MOD/layers/disc${disc}.layer.json"
  if [ -f "$layer" ]; then
    python3 scripts/apply_layer.py \
      "$parent" "$layer" -o "cache/$MOD/FINALFANTASY7_D${disc}.bin"
  else
    cp "$parent" "cache/$MOD/FINALFANTASY7_D${disc}.bin"
  fi
done
```

### Edit

Mods here are binary changes — MIPS stubs and data bytes — not field script
edits. Makou Reactor is the CSR repo's tool for cutting scenes; it has no part
in this loop. Read the code in **Ghidra** to find and confirm the site, then
write the bytes with **ImHex** or any hex editor.

Almost nothing worth patching sits in the raw BIN. The executable code lives in
GZIPPS overlays (`FIELD/FIELD.BIN`, `WORLD/WORLD.BIN`, `BATTLE/BATRES.X`), so a
hex editor pointed at the disc image finds only compressed bytes. Unwrap the
overlay first, patch the decompressed copy, then put it back:

```bash
# 1. lift the overlay out of the disc image, then unwrap it
python3 -c "
from pathlib import Path; import sys; sys.path.insert(0, 'scripts')
from psx_mode2_iso import extract_file
img = Path('cache/$MOD/FINALFANTASY7_D1.bin').read_bytes()
Path('work/BATRES.X').write_bytes(extract_file(img, 'BATTLE/BATRES.X'))"
python3 scripts/decompress_gzipps.py work/BATRES.X work/BATRES.X.dec

# 2. Ghidra on work/BATRES.X.dec to locate the site; ImHex to edit the bytes

# 3. rewrap and inject; the recompressed overlay must fit its original slot
python3 scripts/compress_gzipps.py work/BATRES.X.dec work/BATRES.X work/BATRES.X.new
```

Injection is `replace_file_padded` from `scripts/psx_mode2_iso.py`, which
zero-pads back into the same sector allocation so no later extent moves. The
per-mod scripts under `mods/<name>/scripts/` already do this end to end and are
the best reference; a stub whose length changes needs the whole overlay path,
not a byte poke.

Editing a fixed-length stub in place — same site, same length, new arithmetic —
is the easy case: patch the `.dec`, recompress, inject. Anything that moves code
around needs the JAL targets rechecked in Ghidra first.

### Repair and publish

Then repair footers and publish each disc:

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

`all` always includes `clean`; a complete rebuild should not silently leave
one published base untouched.

Recuts each overlay against the current bases, stamps `baseVersion`, and leaves
`builder/` dirty for you to review and commit. Recuts run one at a time, and
the first failure stops the run: a half-recut pack keeps its old `baseVersion`
and would quietly disappear from the builder. Verify is a separate command —
do not recut just to check a pack.

Before copying any disc image it checks that zopfli is installed and that git
pins `builder/*.json` to LF, so a misconfigured clone fails in seconds instead
of after a long build.

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
