# Task: build v0.2.9 builder-equivalent bin (New Game hang fix) and playtest

## Why

Both the browser builder's download and a local reconstruction of the same
stack hung at "New Game". Root cause found: the published v0.2.8
`builder/single-disc-on-csr/layers/disc1.layer.json` was diffed against a
stale/corrupted work bin whose `FIELD/FIELD.BIN` failed to decompress
(invalid DEFLATE stream). FIELD.BIN is read on every field load, including
the very first one, so this hung New Game on every build using that layer —
independent of the BLACKBGB/LOST2 fixes, which were unaffected and remain
correct.

Fixed with a **hybrid layer**: took v0.2.8's known-good, verified
`FIELD/BLACKBGB.DAT` splice as the base image, and patched in only a
corrected `FIELD/FIELD.BIN` + `WORLD/WORLD.BIN` (confirmed to decompress
cleanly) from a freshly-built work bin. This avoids the automated DSKCG
re-encoder, which a plain flag-less rebuild would otherwise fall back to and
which still hangs the D1→D2 transition. Verified the new layer, reapplied
onto the CSR v0.14.2 base, reproduces the hybrid image byte-for-byte, and
that `FIELD.BIN`/`WORLD.BIN` decompress correctly with `BLACKBGB.DAT`
unchanged from the verified splice.

**Already confirmed locally**: New Game loads and the D1→D2 BLACKBGB
transition works on DuckStation with this rebuild. This task now just needs
you to confirm the same on your machine, and separately test the actual
browser builder-site download (not just this local reconstruction).

## Steps (copy-paste, in order)

### 1. Update both repos

```bash
cd Final-Fantasy-7-Modding
git pull --ff-only
cd ../Final-Fantasy-7-CSR
git pull --ff-only
```

### 2. Clear the stale CSR base cache

This file is gitignored and safe to delete — it's just a local reconstruction
cache, not tracked game content.

```bash
rm -f cache/csr/FINALFANTASY7_D1.bin
```

### 3. Rebuild the builder-equivalent bin

Run from `Final-Fantasy-7-Modding`. Requires
`workspace/pristine/FINALFANTASY7_D1.bin` (your own retail NTSC-U Disc 1
copy) to already be present.

```bash
cd ../Final-Fantasy-7-Modding
python3 scripts/verify_builder_config.py --pristine workspace/pristine/FINALFANTASY7_D1.bin --disc 1 --base csr-v0.14.2 --addon single-disc-on-csr -o workspace/iso-extract/single-disc-builder-v029.bin
```

Expected output ends with:

```
PASS — builder config applies cleanly (151318 total records)
```

If it instead prints `layer mismatch in disc1.layer.json @ ...`, stop and
paste the full output back — that means the cache is stale again or there's
a real layer/base incompatibility, not the issue this task fixes.

### 4. Playtest

Load `workspace/iso-extract/single-disc-builder-v029.bin` in DuckStation.
Start a New Game and confirm it loads correctly (this is the exact stack the
builder site produces: CSR `csr-v0.14.2` base + `single-disc-on-csr` v0.2.9,
nothing else auto-included). If it loads, please also play through to the
D1→D2 transition (BLACKBGB) again to reconfirm that fix still holds.

### 5. Also test the actual builder-site download

Go to https://individualcontributor.dev/builder/, build the same stack
(CSR `csr-v0.14.2` + `single-disc-on-csr`), download the zip, and run:

```bash
python3 scripts/verify_built_disc.py path/to/extracted-download-folder
```

Then playtest that `.bin` the same way (New Game + D1→D2). This confirms the
real download matches the local reconstruction above, not just the script
output.

## Evidence to paste back when done

- Full terminal output of step 3 (the `verify_builder_config.py` run)
- Whether "New Game" loads correctly in DuckStation (local build)
- Whether "New Game" + D1→D2 loads correctly from the builder-site download
- If anything hangs/fails: exactly where (black screen, specific field,
  crash, etc.)

## Reference: prior fix (BLACKBGB/LOST2)

See `docs/findings/2026-08-23-blackbgb-splice-lost2-lzs-fix-verified.md` for
the resolved BLACKBGB D1->D2 hang + LOST2 corruption fixes (both confirmed
on DuckStation emulator; not yet tested on real hardware).

## Reference: BLACKBGB manual-edit splice

The automated DSKCG (ask-for-disc) removal for BLACKBGB still hangs the
D1->D2 transition even after the bit-exact LZS encoder fix, for reasons not
yet root-caused (see follow-ups in the finding above). `build_work_bin.py`'s
default pipeline already works around this by splicing in a known-working
manually-edited `FIELD/BLACKBGB.DAT` (edited in Makou Reactor with the
DSKCG ops removed, confirmed working on DuckStation) instead of re-encoding
it. The commands below are only needed if you want to update that spliced
file from a new manual edit:

```
python3 mods/single-disc/scripts/extract_field_from_bin.py path/to/your-working-manual-edit.bin --field BLACKBGB -o workspace/iso-extract/BLACKBGB.manual.dat
python3 mods/single-disc/scripts/build_work_bin.py -o OUT.bin --blackbgb-manual-bin workspace/iso-extract/BLACKBGB.manual.dat
```

`--blackbgb-manual-bin` accepts either a full disc `.bin` or a raw extracted
`.DAT` (auto-detected by whether the file size is a multiple of 2352).
