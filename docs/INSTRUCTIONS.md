# Task: Test D1->D2 transition with only the ONE relevant DSKCG removed (with proper jump fixup)

## Why

Manual testing in Makou Reactor narrowed the bug down precisely: the
old automated `remove_dskcg.py` removed **all 4** DSKCG opcodes in
BLACKBGB's `init` slot 0 and recalculated jumps around all 4 — that
build hangs on the D1->D2 transition and later shows "Invalid Archive"
in Makou. But manually deleting **only the one** DSKCG on the actual
D1->D2 execution path (leaving the other 3 untouched) works perfectly
and saves fine in Makou.

`remove_dskcg.py` now supports removing a specific occurrence index
of DSKCG per script slot (`only_indices` param), with full, correct
jump-offset fixup (the earlier no-fixup debug build was rejected
since it left the script visibly broken/misaligned in Makou Reactor —
this restores proper fixup math). `build_work_bin.py` now calls
`apply_dskcg_removal(img, only_indices={0})` by default, removing only
occurrence index 0 (the first DSKCG encountered in the script, which
is the one on the D1->D2 path) and leaving the other 3 as-is, matching
your manual fix exactly.

## Prerequisites

- `workspace/pristine/FINALFANTASY7_D1.bin`, `_D2.bin`, `_D3.bin` present.
- `Final-Fantasy-7-CSR` repo checked out as a sibling of this repo.
- Python 3 on PATH; run all commands from this repo's root.

## What you do

1. `git pull --ff-only`.
2. Rebuild the work bin and a matching `.cue`:

   ```bash
   python3 mods/single-disc/scripts/build_work_bin.py -o workspace/iso-extract/single-disc-dskcg-single-occ-test.bin
   printf 'FILE "single-disc-dskcg-single-occ-test.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > workspace/iso-extract/single-disc-dskcg-single-occ-test.cue
   ```

   Expect this line during the DSKCG-removal step:
   ```
   Removing DSKCG (ask-for-disc) ops via live splicer for ['BLACKBGB'] (only occurrence(s) [0])...
       init slot 0: Removed 1 DSKCG
   ```
   No `WARNING:` or uncaught errors.

3. Open `workspace/iso-extract/single-disc-dskcg-single-occ-test.cue` in
   DuckStation fresh (no save states, no cheats).
4. New game, play through Midgar to confirm baseline sanity (no hangs).
5. Progress to the Disc 1->2 transition (BLACKBGB field #103 -> LOST2
   -> break scene -> COS_BTM2). Confirm it goes straight through with
   no black-screen hang and no disc-swap prompt (this should now match
   your manual single-opcode-deletion fix exactly).
6. Open this bin in Makou Reactor and check BLACKBGB field #103.
   Confirm it opens cleanly (no "Invalid Archive"), and that the
   script displays with clean "Goto label X" jumps (no "Forward N
   byte(s)" raw offsets).

## Evidence (paste)

```
D1->2 transition with single-occurrence DSKCG removal: NO HANG / HANGS
Makou Reactor BLACKBGB open: OK / Invalid Archive
Script jumps display as clean labels: YES / NO (describe)
notes:
```

## When done

Paste evidence above, commit this file, push, say check.

---

# Task: Manual WHITE2 (#643) fix in CSR itself, then rebuild single-disc

## Why

You want to fix WHITE2's second movie-hang (`cl`/31) by hand in Makou
Reactor, at the source — CSR's own Disc 2 — instead of patching it in
this repo's `single-disc` pipeline. Once CSR's Disc 2 layer is fixed,
`single-disc`'s `build_work_bin.py` pulls CSR Disc 2 via
`disc_sources.load_csr_image(2)` (pristine D2 + CSR's `disc2.layer.json`),
so the fix flows through automatically on the next single-disc rebuild
— no changes needed in this repo's field-patch scripts.

This is a **manual, human-run process** across two repos. Follow every
step in order; nothing here is scripted end-to-end.

## Part 1 — Edit WHITE2 in CSR's Disc 2 image (Makou Reactor)

1. In `Final-Fantasy-7-CSR`, `git pull --ff-only`.
2. Open `Final-Fantasy-7-CSR/cache/csr/FINALFANTASY7_D2.bin` in Makou
   Reactor (this is the exact edited D2 image CSR's current
   `csr-v0.14.1` Disc 2 layer was diffed from, and what single-disc
   pulls from on every rebuild).
3. Find field 643, `WHITE2.DAT`, script slot `cl` / 31 (the longer
   Cosmo Canyon cutscene script — the one carrying CSR's story `JMPF`
   edit). Remove the `PMVIE`/`MOVIE` opcode pair from that slot only.
   Leave every other opcode in that script (including the `JMPF`
   edit) untouched.
4. Save in Makou. Confirm it succeeds (this is a size-neutral-or-not
   edit on stock CSR D2 — either way should save fine per the earlier
   Makou save investigation).

## Part 2 — Rebuild CSR's Disc 2 layer from the edited image

Still in `Final-Fantasy-7-CSR`:

```bash
python3 scripts/build_csr_base_layers.py cache/csr --version 0.14.2 --discs 2
```

This diffs `pristine/FINALFANTASY7_D2.bin` vs. the edited
`cache/csr/FINALFANTASY7_D2.bin`, writes
`builder/csr-v0.14.2/layers/disc2.layer.json` (a **new** versioned
folder — it will not overwrite `csr-v0.14.1` in place), and verifies
the layer reapplies cleanly onto pristine to reproduce your edited
image byte-for-byte.

`csr-v0.14.2` will only have a Disc 2 layer written by this run — Disc
1 and Disc 3 layers must still come from `csr-v0.14.1` (copy those two
files into `builder/csr-v0.14.2/layers/` and merge `pack.json`'s
`discs` map, or re-run the script with `--discs 1,2,3` against the
full `cache/csr/` set if Disc 1/3 there are already current).

Commit the new `builder/csr-v0.14.2/` folder and the updated
`builder/manifest.json` bases entry (JSON only — never `.bin`/`.cue`)
in the CSR repo, then push.

## Part 3 — Point single-disc at the new CSR version

Back in this repo (`Final-Fantasy-7-Modding`):

1. Update every `csr-v0.14.1` reference relevant to single-disc to
   `csr-v0.14.2`:
   - `scripts/disc_sources.py`: `csr_layer()`'s
     `"builder/csr-v0.14.1/layers"` path.
   - `builder/single-disc-on-csr/pack.json` and the manifest entry's
     `compatibleBases`.
   - Any other `single-disc*` pack/manifest entries with
     `compatibleBases: ["csr-v0.14.1"]`.
2. Rebuild the single-disc work bin and regenerate its layer exactly
   as in past releases (`build_work_bin.py` → `bin_diff_to_layer.py`
   against pristine D1) — this should no longer need
   `fix_white2_movie_hang.py`'s `cl`/31 branch since the fix now comes
   from CSR's own Disc 2 layer. Confirm no `PMVIE`/`MOVIE` remain in
   WHITE2 via the same verification snippet used for v0.2.5 (extract
   `FIELD/WHITE2.DAT` from pristine+CSR+single-disc-layer and check
   `decode_ops` for any `PMVIE`/`MOVIE`).
3. Bump `single-disc-on-csr`'s version, update CHANGELOG, run
   `verify_builder_config.py --base csr-v0.14.2 --addon single-disc-on-csr`,
   commit, push.

## When done

Confirm each part above, then playtest WHITE2 end-to-end as in prior
releases (loads, plays through, no freeze) and re-confirm Makou save
still works on the new single-disc build. Paste evidence, commit,
push, say check.

---

# Task: Playtest single-disc-on-csr v0.2.5 (fixes 2nd WHITE2 #643 movie hang)

## Why

You reported field 643 (WHITE2) didn't load at all on the v0.2.4 build.
Root cause: WHITE2 has **two independent** script slots that each try
to play a field movie. v0.2.4 only fixed one of them (`mdir` slot 31).
The other (`cl` slot 31 — CSR Disc 2's longer Cosmo Canyon cutscene
script, which also carries a CSR story edit) still had its own
`PMVIE`/`MOVIE` pair, and that movie ID doesn't resolve to a valid
stream on the single-disc build either — so the field hung on load
exactly like before.

Fix: strip only the `PMVIE`/`MOVIE` opcodes from `cl` slot 31, keeping
every other opcode (including CSR's story edit) untouched. Verified
directly against the actual builder pipeline (pristine D1 + CSR base +
this layer) that WHITE2 now has zero `PMVIE`/`MOVIE` opcodes anywhere.

Bumped to **v0.2.5**. This is a fresh playtest — confirm WHITE2 now
loads and plays correctly, and that everything from v0.2.4 still holds.

The build isn't committed (`.bin`/`.cue` gitignored) — rebuilt locally
below.

## Prerequisites

- `workspace/pristine/FINALFANTASY7_D1.bin`, `_D2.bin`, `_D3.bin` present.
- `Final-Fantasy-7-CSR` repo checked out as a sibling of this repo.
- Python 3 on PATH; run all commands from this repo's root.

## What you do

1. `git pull --ff-only`.
2. Rebuild the work bin and a matching `.cue`:

   ```bash
   python3 mods/single-disc/scripts/build_work_bin.py -o workspace/iso-extract/single-disc-v025-repro.bin
   printf 'FILE "single-disc-v025-repro.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > workspace/iso-extract/single-disc-v025-repro.cue
   ```

   Expect two lines during the "Fixing WHITE2 movie hang" step: one for
   `mdir/31` (IFSW/PMVIE/JMPF/PMVIE/MOVIE block removed) and one for
   `cl/31` (PMVIE/MOVIE opcodes removed). No `WARNING:` or uncaught
   errors.

3. Open `workspace/iso-extract/single-disc-v025-repro.cue` in
   DuckStation fresh (no save states, no cheats).
4. New game, play through Midgar to confirm baseline sanity (no hangs).
5. Progress to the Disc 1→2 transition (BLACKBGB field #103 → LOST2 →
   break scene → COS_BTM2). Confirm it still goes straight to the break
   scene with music, and LOST2's background still renders correctly
   (unchanged from v0.2.3/v0.2.4).
6. Reach Cosmo Canyon and enter WHITE2. Confirm the field now loads at
   all (previously it didn't load), and that any cutscene/character
   moment there plays through without freezing or glitching.
7. Open this bin in Makou Reactor, make a trivial edit, Save. Confirm
   it still succeeds (should be unchanged from v0.2.3/v0.2.4).

## Evidence (paste)

```
Disc 1->2 transition: straight to break scene with music (expected)
LOST2 background: renders correctly (expected)
WHITE2: loads and plays through normally (fixed) / still hangs or glitches (bug)
Makou save test: SUCCEEDED / FAILED (paste exact text)
notes:
```

## When done

Paste evidence above, commit this file, push, say check.
