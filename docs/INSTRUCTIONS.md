# Task: build single-disc with ending movies re-enabled, playtest the LASTMAP ending

## Why

`LASTMAP` (field 768) `AD3` script 31 freezes after the "Ask Question"
choice: the `MOVIE`/`FMUSC` opcodes there expect an ending/credits movie
that wasn't actually on the single-disc image. The `single-disc-endings-
v0.1.0-part1..7` layers (the movie asset pack) had their manifest
`autoIncludeWhen` trigger swapped for a dead sentinel back in v0.2.8, so
they silently never included on any single-disc build despite the
manifest blurb claiming "Always applied... Not optional."

Fixed: `single-disc-endings-v0.1.0-part1..7` now auto-include again
whenever `single-disc-on-csr` is selected. Manip movies
(`single-disc-csr-manip-movies-v0.1.4`/`v0.1.5`) are intentionally kept
disabled for this test — testing endings in isolation first.

**Not yet playtested** — that's this task.

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

### 3. Rebuild the builder-equivalent bin (endings only, no manip movies)

Run from `Final-Fantasy-7-Modding`. Requires
`workspace/pristine/FINALFANTASY7_D1.bin` (your own retail NTSC-U Disc 1
copy) already present.

```bash
python3 scripts/verify_builder_config.py --pristine workspace/pristine/FINALFANTASY7_D1.bin --disc 1 --base csr-v0.14.2 --addon single-disc-on-csr --addon single-disc-endings-v0.1.0-part1 --addon single-disc-endings-v0.1.0-part2 --addon single-disc-endings-v0.1.0-part3 --addon single-disc-endings-v0.1.0-part4 --addon single-disc-endings-v0.1.0-part5 --addon single-disc-endings-v0.1.0-part6 --addon single-disc-endings-v0.1.0-part7 -o workspace/iso-extract/ff7_d1_singledisc_endings_playtest.bin
```

Expected output starts with a cache line — either:

```
cache miss — apply disc1.layer.json onto pristine → cache/csr/D1
wrote .../Final-Fantasy-7-CSR/cache/csr/FINALFANTASY7_D1.bin (...)
```

(first run after clearing cache) or `cache hit: ...` (if you didn't
change CSR and didn't clear cache — fine to skip step 2 in that case).
Then ends with:

```
PASS — builder config applies cleanly (3422768 total records)
```

**Do not** open the output `.bin` directly in Makou Reactor to hand-edit
it — it's a raw disc image, not something Makou Reactor can save back to
("Cannot update game binaries" / "invalid archive" errors are from
trying to do this). All edits happen on the CSR side (Makou Reactor on
the CSR disc image → rebuild CSR's own layer JSON → push), then this
script re-applies that layer onto Disc 1 from scratch.

### 4. Create the matching .cue (if not already present)

```bash
cat > workspace/iso-extract/ff7_d1_singledisc_endings_playtest.cue << 'EOF'
FILE "ff7_d1_singledisc_endings_playtest.bin" BINARY
  TRACK 01 MODE2/2352
    INDEX 01 00:00:00
EOF
```

### 5. Playtest

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

- Full terminal output of step 3 (the `verify_builder_config.py` run,
  including the cache miss/hit line)
- Whether the `LASTMAP` "Ask Question" freeze is gone
- Whether the ending/credits movies play correctly end to end
- Regression check results (New Game / D1→D2 / break scene)
- If anything hangs/crashes: exactly where (field, script line, symptom)
