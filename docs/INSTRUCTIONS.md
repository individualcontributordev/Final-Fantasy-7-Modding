# Task: build v0.2.11 (Disc 3 ending movie-opcode fix) and playtest the ending

## Why

The Disc 3 ending sequence crashed because fields 765-768 (`LAS4_2`,
`LAS4_3`, `LAS4_4`, `LASTMAP`) contain `PlayMovie` opcodes for movie files
that don't exist in the Disc 1 single-disc LBA map. You fixed this in CSR
by editing those 4 fields in Makou Reactor to move (not delete) the
opcodes, playtested it working on CSR disc 3 alone, then built and pushed
the updated `disc3.layer.json` (commit `9ad13bb`) to `Final-Fantasy-7-CSR`.

Single-disc's field-merge pipeline pulls `LAS4_2`/`LAS4_3`/`LAS4_4`/
`LASTMAP` from CSR Disc 3 automatically (they're CSR-D3-only edits vs
pristine, matching pristine on D1/D2), so no script changes were needed —
just a rebuild + re-diff against the updated CSR base. Verified locally:
the rebuilt work bin round-trips byte-for-byte through the new
`disc1.layer.json`, and `verify_builder_config.py` passes.

**Not yet playtested past the Disc 3 ending sequence on DuckStation** —
that's this task.

## Steps (copy-paste, in order)

### 1. Update both repos

```bash
cd Final-Fantasy-7-Modding
git pull --ff-only
cd ../Final-Fantasy-7-CSR
git pull --ff-only
```

### 2. Clear the stale CSR base cache

```bash
rm -f cache/csr/FINALFANTASY7_D1.bin
```

### 3. Rebuild the builder-equivalent bin

Run from `Final-Fantasy-7-Modding`. Requires
`workspace/pristine/FINALFANTASY7_D1.bin` (your own retail NTSC-U Disc 1
copy) already present.

```bash
cd ../Final-Fantasy-7-Modding
python3 scripts/verify_builder_config.py --pristine workspace/pristine/FINALFANTASY7_D1.bin --disc 1 --base csr-v0.14.2 --addon single-disc-on-csr -o workspace/iso-extract/single-disc-builder-v0211.bin
```

Expected output ends with:

```
PASS — builder config applies cleanly (151093 total records)
```

### 4. Playtest

Load `workspace/iso-extract/single-disc-builder-v0211.bin` in DuckStation
(exact stack the builder site produces: CSR `csr-v0.14.2` base +
`single-disc-on-csr` v0.2.11, nothing else auto-included).

- Confirm New Game still loads, D1→D2 transition and break scene still
  work (regression check — should be unaffected by this change).
- Play (or save-state-skip) through to the Disc 3 ending sequence.
- **Confirm the ending plays through without crashing** at the point
  where fields `LAS4_2`/`LAS4_3`/`LAS4_4`/`LASTMAP` run — this is the new
  fix this task verifies.

### 5. Also test the actual builder-site download

Go to https://individualcontributor.dev/builder/, build the same stack
(CSR `csr-v0.14.2` + `single-disc-on-csr`), download the zip, and run:

```bash
python3 scripts/verify_built_disc.py path/to/extracted-download-folder
```

Then playtest that `.bin` through the ending the same way.

## Evidence to paste back when done

- Full terminal output of step 3 (the `verify_builder_config.py` run)
- Whether New Game / D1→D2 / break scene still work (regression check)
- Whether the Disc 3 ending sequence now plays through without crashing,
  locally and from the builder-site download
- If anything hangs/crashes: exactly where (black screen, specific field,
  crash, etc.)
