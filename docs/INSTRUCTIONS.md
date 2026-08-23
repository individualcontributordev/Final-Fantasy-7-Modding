# Task: build v0.2.10 (break-scene fix) and playtest past the D1→D2 transition

## Why

After the v0.2.9 "want to save?" prompt, the Cosmo Canyon break scene
(LOST2, field 634) failed to load. Root cause: v0.2.9's layer was built by
hand-stitching the v0.2.8 layer's `FIELD/BLACKBGB.DAT` onto a separately
fixed `FIELD.BIN`/`WORLD.BIN`, then re-diffing. That stitching corrupted
`FIELD/LOST2.DAT`'s internal 7-section offset table (walkmesh/background/
model_loader boundaries shifted) even though the file's overall size still
matched CSR D2 — Makou Reactor showed it as corrupted, and the break-scene's
`IFUW GameMoment==0xa455 -> MAPJUMP COS_BTM2` trigger never ran.

Fixed by rebuilding from scratch in one pass (no hybrid stitching): a
single `build_work_bin.py` run (all field merges + verified BLACKBGB manual
splice + SNOVA inject + FIELD.BIN/WORLD.BIN table fix) diffed directly
against the CSR v0.14.2 base. The manual-edit `FIELD/BLACKBGB.DAT` splice
is now committed at `mods/single-disc/patches/BLACKBGB.manual.dat` and used
by default, so this no longer depends on a human-supplied local file.

**Verified locally**: `FIELD/LOST2.DAT` byte-identical to CSR D2 (correct
section sizes), `FIELD/BLACKBGB.DAT` byte-identical to the verified manual
splice, `FIELD.BIN`/`WORLD.BIN` decompress cleanly, and reapplying the new
layer onto the CSR base reproduces the work bin byte-for-byte. **Not yet
playtested past the break scene on DuckStation** — that's this task.

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
python3 scripts/verify_builder_config.py --pristine workspace/pristine/FINALFANTASY7_D1.bin --disc 1 --base csr-v0.14.2 --addon single-disc-on-csr -o workspace/iso-extract/single-disc-builder-v0210.bin
```

Expected output ends with:

```
PASS — builder config applies cleanly (151025 total records)
```

If it instead prints `layer mismatch in disc1.layer.json @ ...`, stop and
paste the full output back — that means the cache is stale again or there's
a real layer/base incompatibility, not the issue this task fixes.

### 4. Playtest

Load `workspace/iso-extract/single-disc-builder-v0210.bin` in DuckStation
(this is the exact stack the builder site produces: CSR `csr-v0.14.2` base +
`single-disc-on-csr` v0.2.10, nothing else auto-included).

- Start a New Game and confirm it loads.
- Play through to the D1→D2 transition, confirm the "want to save?" prompt
  and BLACKBGB transition still work (as in v0.2.8/v0.2.9).
- **Confirm the Cosmo Canyon break scene (LOST2) now loads and plays after
  the save prompt** — this is the new fix this task verifies.

### 5. Also test the actual builder-site download

Go to https://individualcontributor.dev/builder/, build the same stack
(CSR `csr-v0.14.2` + `single-disc-on-csr`), download the zip, and run:

```bash
python3 scripts/verify_built_disc.py path/to/extracted-download-folder
```

Then playtest that `.bin` the same way (New Game → D1→D2 → break scene).
This confirms the real download matches the local reconstruction above.

## Evidence to paste back when done

- Full terminal output of step 3 (the `verify_builder_config.py` run)
- Whether "New Game" loads correctly in DuckStation (local build)
- Whether the D1→D2 transition (BLACKBGB) and break scene (LOST2) both
  play correctly, locally and from the builder-site download
- If anything hangs/fails: exactly where (black screen, specific field,
  crash, etc.)

## Reference: prior fixes

- `docs/findings/2026-08-23-blackbgb-splice-lost2-lzs-fix-verified.md` —
  BLACKBGB D1→D2 hang + original LOST2 LZS-corruption fixes.
- `docs/findings/2026-08-23-v028-new-game-hang-corrupted-field-bin-layer.md`
  — v0.2.8→v0.2.9 New Game hang (corrupted FIELD.BIN in the shipped layer).

The `FIELD/BLACKBGB.DAT` manual-edit splice is now committed at
`mods/single-disc/patches/BLACKBGB.manual.dat` and used by default by
`build_work_bin.py` — no extra flag or local file needed. Pass
`--blackbgb-manual-bin path/to/file` to override with a new manual edit, or
`--skip-dskcg-removal` to fall back to the (currently broken) automated
DSKCG re-encoder.
