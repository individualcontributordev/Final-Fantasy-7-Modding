# Layer Engineering — the `ic-layer-v1` format

How a `.bin` edit becomes a browser-deliverable pack. For **CLI usage**
(commands to run) see `docs/08-engineer-build-guide.md` — this doc explains
the **file format itself** and walks one diff byte-for-byte so you could
write a compatible tool from scratch, per `.agents/rules/verified-reference-evidence.mdc`.

## Why a layer, not a patched .bin

Players download a base disc (retail or a CSR release) once. Every mod ships
only the **bytes that differ** from that base, as JSON, applied client-side
in the browser. This avoids distributing copyrighted disc images and lets
mods stack (encounter rate + single-disc + scene trims, etc.) without each
combination needing its own multi-GB file.

## `ic-layer-v1` schema (evidence: `scripts/bin_diff_to_layer.py`, `scripts/apply_layer.py`)

```json
{
  "format": "ic-layer-v1",
  "id": "field-encounter-25-v0.1.2-disc1",
  "description": "Field FORCE stub Disc 1",
  "target": "disc-image",
  "stats": {
    "originalBytes": 748775664,
    "modifiedBytes": 748775664,
    "changedBytes": 214,
    "records": 3
  },
  "records": [
    { "offset": 630784, "hex": "0c00a1a1" }
  ]
}
```

| Field | Meaning |
|---|---|
| `format` | Must be exactly `"ic-layer-v1"` — `apply_layer.py` rejects anything else |
| `target` | Must be `"disc-image"` or omitted |
| `records[].offset` | Absolute byte offset into the **base** image this layer targets |
| `records[].hex` | Replacement bytes at that offset, lowercase hex string, no `0x` |
| `stats.originalBytes` | Size of the base image the diff was computed against — **critical**: a layer's records are only valid applied to a base of exactly this size/identity. Applying v0.1.5 (diffed against v0.1.4's output) directly onto a different base silently writes wrong-offset garbage with no error (see `docs/findings/2026-08-24-csr-movie-reachability-scan.md`, "build_playtest_bin.py only applied v0.1.5" — a real incident from this exact mistake) |
| `stats.changedBytes` / `records` | Informational only, not read by the applier |

Runs of changed bytes are coalesced into one record each (`iter_runs()` in
`bin_diff_to_layer.py`) rather than one record per byte — keeps JSON small.
`MAX_RECORD_BYTES = 4096` caps a single record so huge changed spans (e.g. a
relocated movie) split into multiple sequential records instead of one giant
string.

## Growth handling

If `modified` is **larger** than `original` (e.g. EOF-appended movie data),
`apply_layer.py` extends the image with zero bytes before writing records
that land past the original end, and does not require every trailing zero
byte to be an explicit record — `stats.modifiedBytes` documents the intended
final size.

## Manifest wiring (`builder/manifest.json`)

A layer file on disk is inert until an entry in `manifest.json` points a
disc number to it and declares which bases it's valid against:

```json
{
  "id": "field-encounter-25-v0.1.2",
  "format": "ic-layer-v1",
  "exclusiveGroup": "field-encounter-rate",
  "compatibleBases": ["clean"],
  "discs": { "1": "./field-encounter-25-v0.1.2/layers/disc1.layer.json" },
  "enabled": true
}
```

| Field | Meaning |
|---|---|
| `compatibleBases` | Base pack `id`s (from the CSR repo's manifest, e.g. `clean`, `csr-v0.14.2`, `highwind-v0.2.0`) this layer's `records` are valid against. Diffing against the wrong base silently corrupts other players' builds — always diff against exactly what `compatibleBases` claims |
| `exclusiveGroup` | Only one add-on per group may be selected (e.g. only one encounter rate) |
| `autoIncludeWhen` | Auto-stacks this add-on when another id is selected — **does not check `enabled: false`**, a known gotcha (`docs/08-engineer-build-guide.md`) |
| `discs` | Map of disc number → relative path to that disc's layer JSON |

## Worked example: diffing a movie relocation into a layer

Continuing the movie-relocation example from `docs/reference/movie-system.md`:

1. You have `work.bin` (patched: RCKTOFF.MOV relocated + `MOVIE_ID.BIN` row 41 updated) and the same-size `base.bin` (single-disc core, pre-patch).
2. Diff:
   ```bash
   python3 scripts/bin_diff_to_layer.py \
     workspace/iso-extract/base.bin \
     workspace/iso-extract/work.bin \
     -o builder/single-disc-on-csr/layers/disc1.layer.json \
     --id single-disc-on-csr-disc1 \
     --description "Add RCKTOFF.MOV relocation"
   ```
   This walks both files in 1 MiB chunks (`iter_runs()`), finds every
   differing byte run (the new movie sectors + the 20 changed
   `MOVIE_ID.BIN` bytes + the dirent LBA/size fields), and emits one record
   per contiguous run.
3. Verify round-trip before publishing:
   ```bash
   python3 scripts/apply_layer.py base.bin disc1.layer.json --expect work.bin
   # prints "OK — layer apply matches --expect" or the exact mismatch offset
   ```
4. Only then bump the manifest version and commit — `apply_layer.py --expect`
   is the same code path the browser builder uses, so a pass here means the
   live site will reproduce `work.bin` exactly for any player who selects
   this add-on on the declared `compatibleBases`.

## Common failure modes (all previously hit in this repo)

| Symptom | Cause | Fix |
|---|---|---|
| Byte survives under a layer that should have changed it | Diffed against the wrong base (e.g. pristine when the pack's real base is a CSR release) — coincidental byte match with old base produces no record | Re-diff against the exact `compatibleBases` image |
| Field parses garbage after applying a versioned add-on alone | Layer is a **delta pack** computed against a prior version's *output*, not the core base (`stats.originalBytes` won't match) | Apply all prerequisite layers in the documented order first |
| Applied image doesn't match live site | Missing an `autoIncludeWhen`-triggered addon in your local `verify_builder_config.py --addon` flags | Pass every addon id explicitly; the CLI does not auto-stack |
| Makou Reactor says **"Invalid archive"** when saving any edit on a built `.bin` | You (or a build script) resized one or more individual `FIELD/*.DAT` files in place via `replace_file_within_sectors()` (which patches only the ISO9660 directory record) but never patched **FIELD.BIN's/WORLD.BIN's own embedded `(location, size)` lookup table**. ff7tk's `IsoArchiveFF7::updateBin()` re-scans that embedded table on every save; a stale entry means it can't find the field at its new size and the save fails with `InvalidError`. See `Final-Fantasy-7-Modding/mods/single-disc/scripts/fix_field_bin_table.py` docstring for the full root-cause writeup. | Any time your build resizes individual `FIELD/*.DAT` (or `WORLD/*`) files — not the whole `FIELD.BIN`/`WORLD.BIN` blob at once — run `fix_field_and_world_bins(img)` (from `fix_field_bin_table.py`) as the **last** patching step before diffing to a layer. Whole-container rebuilds (e.g. `field-random-encounters`, which replaces the entire `FIELD/FIELD.BIN` slot with a self-consistent rebuilt blob) are not affected and don't need this step. |

## Sources

- `scripts/bin_diff_to_layer.py`
- `scripts/apply_layer.py`
- `builder/manifest.json`
- `docs/08-engineer-build-guide.md` (CLI usage)
- `docs/findings/2026-08-24-csr-movie-reachability-scan.md` (real delta-pack incident)
