# Task: confirm LASTMAP freeze fixed, then build+playtest the full ending/credits movie sequence

## Why

Your CSR Disc 3 `PMVIE` removal worked — the `LASTMAP` `AD3` script 31
freeze is fixed on the CSR side. Verified directly in the fresh CSR D3
field data: `AD` script 4's `PMVIE f818` (which set MOVIE_ID row 24 to
`LASTFLOR.MOV`) is now gone entirely, and `AD3` script 31 goes straight
`REQ → BMUSC → FMUSC` with no `MOVIE`/`PMVIE` op left at all. That means
**`LASTFLOR.MOV` is no longer needed in the single-disc endings movie
layer** — it was only ever aliased onto D1 for that now-dead opcode.

Removed the now-dead `LASTFLOR.MOV → MAINPLR.MOV` alias job from
`mods/single-disc/scripts/alias_d3_ending_lbas_on_d1.py` (confirmed no
other field DAT sets MOVIE_ID row 24 except a handful of early D1
fields that rely on its untouched *default* value — `MAINPLR.MOV` —
so leaving row 24 alone is correct, not just harmless).

The remaining ending/credits movie aliases (`ONTRAIN→LASTMAP.BIN`,
`SMK→ENDING01`, `SOUTHMK→ENDING3E`, `MONITOR→ENDING2E`, plus the
`CANONON`/`LAST4_3` splices) are untouched. This task rebuilds the full
single-disc pipeline (fresh CSR D1/D2/D3 → merged work bin → re-diffed
`single-disc-on-csr` layer) and then builds+plays the **actual ending
movie sequence bin** (`build_ending_credits_test_bin.py`, not just the
endings-parts layers) to verify the whole sequence plays through
without the LASTFLOR alias.

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
python3 scripts/build_csr_d1_base.py
```

This applies CSR's current `builder/csr-v0.14.2/layers/disc1.layer.json`
onto pristine D1 and writes it to `workspace/tmp/csr_d1_base.bin`
(gitignored). Expect `wrote 747435024 -> workspace/tmp/csr_d1_base.bin`.

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
python3 scripts/bin_diff_to_layer.py workspace/tmp/csr_d1_base.bin workspace/iso-extract/single-disc-work.bin -o builder/single-disc-on-csr/layers/disc1.layer.json --id single-disc-on-csr-disc1 --description "single-disc-on-csr: rebuilt from latest CSR D1/D2/D3"
```

Expect `records=` in the tens of thousands and no "no differences
found" warning. Bump `builder/single-disc-on-csr/pack.json`'s and
`builder/manifest.json`'s matching entry's `version`/`blurb`/`betaNote`,
and `mods/single-disc/VERSION` + `CHANGELOG.md`, if you intend to commit
this rebuild.

### 6. Build the actual ending/credits movie sequence bin

This is a separate, dedicated ending-movie test bin — not the
endings-parts layers used for the shipped `single-disc-on-csr` addon
stack. It rebuilds `ff7_d1_playtest_csr_sd_movies.bin` first (CSR +
single-disc core + manip-movies), then splices in the D3 ending
streams (via the just-edited `alias_d3_ending_lbas_on_d1.py`, now
without the dead `LASTFLOR.MOV` alias), the `CANONON` lake fix, and the
`LAST4_3`→`GOLD7_2` manip seed.

```bash
python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
```

Runs `build_playtest_bin.py` as step 1/5 internally (uses
`builder/csr-v0.14.2`, `builder/single-disc-on-csr`, and
`builder/single-disc-csr-manip-movies-v0.1.5` — already current, no
edits needed there). Expect all 5 steps to print `OK`/pass lines, no
`FAIL`, ending with:

```
WROTE workspace/iso-extract/ff7_d1_playtest_ending_test.bin
WROTE workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

### 7. Playtest

Open `workspace/iso-extract/ff7_d1_playtest_ending_test.cue` in
DuckStation.

- Get to `LASTMAP` (field 768), entity `AD3`, and trigger the "Ask
  Question" choice (Script 31, line 224).
- **Confirm the scene loads and plays through** instead of freezing —
  this is the bug the new CSR `PMVIE` removal fixed.
- Watch the full ending/credits movie sequence through to the end
  (`ONTRAIN`, `ENDING01`, `ENDING3E`, `ENDING2E`, and the `LOSLAKE1`
  lake scene via the `CANONON` splice) — confirm none of them are
  silent/black or freeze, now that `LASTFLOR.MOV` is no longer aliased.
- Regression check: confirm New Game, D1→D2 transition, and the break
  scene (`LOST2`) are unaffected.

## Evidence to paste back when done

- Full terminal output of steps 4-6 (`build_work_bin.py`,
  `bin_diff_to_layer.py`, and `build_ending_credits_test_bin.py`)
- Whether the `LASTMAP` "Ask Question" freeze is gone
- Whether the ending/credits movies play correctly end to end
- Regression check results (New Game / D1→D2 / break scene)
- If anything hangs/crashes: exactly where (field, script line, symptom)
