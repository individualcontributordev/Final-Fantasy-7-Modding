# Task: rebuild single-disc-on-csr from the full pipeline against the latest CSR, then playtest the LASTMAP ending

## Why

`LASTMAP` (field 768) `AD3` script 31 freezes after the "Ask Question"
choice. Two separate bugs stacked here:

1. The `single-disc-endings-v0.1.0-part1..7` layers (the movie asset
   pack) had their manifest `autoIncludeWhen` trigger swapped for a dead
   sentinel back in v0.2.8, so they silently never included on any
   single-disc build despite the manifest blurb claiming "Always
   applied... Not optional." **Fixed** in a prior task — the 7 parts
   now auto-include whenever `single-disc-on-csr` is selected.
2. A manual CSR Disc 3 edit had routed around the `AD3` script 31
   `PlayMovie`/`FMUSC` opcodes with a goto/label skip (to dodge an
   earlier crash), so even with the movie assets now present the
   opcodes never fired. That CSR edit was reverted (CSR commit
   `965d040`) — both `MOVIE f9` and `FMUSC fc01` are restored intact.
   Because `builder/single-disc-on-csr/layers/disc1.layer.json` is a
   **pre-baked diff** that doesn't auto-refresh when the CSR source
   changes, it had to be rebuilt via `build_work_bin.py` and re-diffed
   (`single-disc-on-csr` v0.2.12) to actually pick up the CSR revert.

Verified via `field_dat.py` that the rebuilt bin's `LASTMAP.DAT` `AD3`
slot 31 now has `MOVIE f9` / `BMUSC f601` / `FMUSC fc01` back-to-back
right after the `REQ 0112c6` disc-check, with no conditional skip.
Manip movies (`single-disc-csr-manip-movies-v0.1.4`/`v0.1.5`) are
intentionally kept disabled for this test — testing endings in
isolation first.

**Not yet playtested on DuckStation** — that's this task.

## Steps (copy-paste, in order)

### 1. Update BOTH repos

The single-disc build reads CSR's Disc 3 layer (your field 768 un-skip
edit) from the `Final-Fantasy-7-CSR` repo, and caches a built copy of it.
If you skip pulling CSR or skip clearing the cache, the build will
silently use a stale/old CSR D1 image and your field 768 edit will not
be in the output — this is the most common cause of "the bin doesn't
reflect my edit."

```bash
cd Final-Fantasy-7-Modding
git pull --ff-only
cd ../Final-Fantasy-7-CSR
git pull --ff-only
cd ../Final-Fantasy-7-Modding
```

### 2. Clear the stale CSR base cache

Required every time the CSR layer changes (e.g. after any Makou Reactor
edit + layer rebuild + push on the CSR side):

```bash
rm -f ../Final-Fantasy-7-CSR/cache/csr/FINALFANTASY7_D1.bin
```

### 3. Rebuild the CSR D1 base image (needed as the diff baseline in step 5)

Requires `workspace/pristine/FINALFANTASY7_D1.bin` (your own retail
NTSC-U Disc 1 copy) already present in `Final-Fantasy-7-Modding`.

```bash
python3 -c "
import sys
sys.path.insert(0, 'scripts')
from disc_sources import load_csr_image
img = load_csr_image(1)
open('/tmp/csr_d1_base.bin', 'wb').write(img)
print('wrote', len(img))
"
```

This applies CSR's current `builder/csr-v0.14.2/layers/disc1.layer.json`
onto pristine D1. Expect `wrote 747435024`.

### 4. Rebuild the merged single-disc work bin

This is the actual "full pipeline" step: it takes CSR D1 (loaded fresh
from `Final-Fantasy-7-CSR`, same as step 3) and merges in every CSR
D2/D3-only field edit (including your `LASTMAP` field 768 revert),
splices the verified `BLACKBGB` DSKCG-removal, patches the `FIELD.BIN`/
`WORLD.BIN` lookup tables, and injects `SNOVA` from pristine D3. See
`mods/single-disc/scripts/build_work_bin.py` module docstring for the
full step-by-step breakdown.

```bash
python3 mods/single-disc/scripts/build_work_bin.py -o workspace/iso-extract/single-disc-work.bin
```

Takes a couple minutes (loads CSR D1/D2/D3 fresh each time — no cache).
Ends with `Done. Final work bin: workspace/iso-extract/single-disc-work.bin`.

### 5. Diff the work bin against the CSR D1 base into the addon layer

This produces the actual `single-disc-on-csr` mod artifact — the file
the builder ships. It overwrites the committed layer, so **only run this
once you're ready to re-verify and re-ship** (see `AGENTS.md` — pack
version/changelog bumps still apply if you commit the result).

```bash
python3 scripts/bin_diff_to_layer.py /tmp/csr_d1_base.bin workspace/iso-extract/single-disc-work.bin -o builder/single-disc-on-csr/layers/disc1.layer.json --id single-disc-on-csr-disc1 --description "single-disc-on-csr: rebuilt from latest CSR D1/D2/D3"
```

Expect `records=` in the tens of thousands and no "no differences
found" warning. Bump `builder/single-disc-on-csr/pack.json`'s and
`builder/manifest.json`'s matching entry's `version`/`blurb`/`betaNote`,
and `mods/single-disc/VERSION` + `CHANGELOG.md`, if you intend to commit
this rebuild.

### 6. Rebuild the builder-equivalent playtest bin (endings only, no manip movies)

Run from `Final-Fantasy-7-Modding`.

```bash
python3 scripts/verify_builder_config.py --pristine workspace/pristine/FINALFANTASY7_D1.bin --disc 1 --base csr-v0.14.2 --addon single-disc-on-csr --addon single-disc-endings-v0.1.0-part1 --addon single-disc-endings-v0.1.0-part2 --addon single-disc-endings-v0.1.0-part3 --addon single-disc-endings-v0.1.0-part4 --addon single-disc-endings-v0.1.0-part5 --addon single-disc-endings-v0.1.0-part6 --addon single-disc-endings-v0.1.0-part7 -o workspace/iso-extract/ff7_d1_singledisc_endings_playtest.bin
```

Expected output starts with a cache line — either:

```
cache miss — apply disc1.layer.json onto pristine → cache/csr/D1
wrote .../Final-Fantasy-7-CSR/cache/csr/FINALFANTASY7_D1.bin (...)
```

(first run after clearing cache) or `cache hit: ...` (if you didn't
clear cache in step 2 — fine, the base CSR D1 doesn't need to be
current for this step since the freshly re-diffed addon layer from
step 5 already carries the latest CSR D2/D3 field edits baked in). Then
ends with:

```
PASS — builder config applies cleanly (3422700 total records)
```

**Do not** open the output `.bin` directly in Makou Reactor to hand-edit
it — it's a raw disc image, not something Makou Reactor can save back to
("Cannot update game binaries" / "invalid archive" errors are from
trying to do this). All edits happen on the CSR side (Makou Reactor on
the CSR disc image → rebuild CSR's own layer JSON → push), then steps
3-5 above rebuild `single-disc-on-csr`'s own layer from scratch.

### 7. Create the matching .cue (if not already present)

```bash
cat > workspace/iso-extract/ff7_d1_singledisc_endings_playtest.cue << 'EOF'
FILE "ff7_d1_singledisc_endings_playtest.bin" BINARY
  TRACK 01 MODE2/2352
    INDEX 01 00:00:00
EOF
```

### 8. Playtest

Open `workspace/iso-extract/ff7_d1_singledisc_endings_playtest.cue` in
DuckStation.

- Get to `LASTMAP` (field 768), entity `AD3`, and trigger the "Ask
  Question" choice (Script 31, line 224).
- **Confirm the scene loads and plays through** instead of freezing with
  stray movie audio — this is the bug this task verifies is fixed.
- Also spot-check the rest of the ending/credits sequence plays cleanly
  (all 7 parts of the movie pack are now included).
- Regression check: confirm New Game, D1→D2 transition, and the break
  scene (`LOST2`) are unaffected.

## Evidence to paste back when done

- Full terminal output of steps 4-6 (`build_work_bin.py`,
  `bin_diff_to_layer.py`, and the `verify_builder_config.py` run
  including the cache miss/hit line)
- Whether the `LASTMAP` "Ask Question" freeze is gone
- Whether the ending/credits movies play correctly end to end
- Regression check results (New Game / D1→D2 / break scene)
- If anything hangs/crashes: exactly where (field, script line, symptom)
