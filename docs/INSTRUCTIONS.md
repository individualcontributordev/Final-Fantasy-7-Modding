## TASK: create a manual-edit bin in Makou Reactor, then dump + compare

### Step 1 — build a base bin with everything EXCEPT the automated DSKCG removal

This matches the real pipeline (rework merge + safe-field merge + FIELD.BIN
table fix + SNOVA inject) but skips the automated DSKCG step, so you can
manually delete the opcode yourself and get an apples-to-apples comparison:

```
python3 mods/single-disc/scripts/build_work_bin.py -o workspace/iso-extract/manual-edit-base.bin --skip-dskcg-removal
```

### Step 2 — open it in Makou Reactor and manually remove the DSKCG opcode

1. Open `workspace/iso-extract/manual-edit-base.bin` in Makou Reactor.
2. Open field `BLACKBGB`, script `init`, slot `0`.
3. Find the `DSKCG` (Ask for disc) opcode inside the branch gated by
   `if var[3][136] bitON 4` (the one you previously confirmed is on the
   D1→D2 path) and delete just that one opcode.
4. Save the field in Makou Reactor, then save/export the .bin (however you
   normally do it — e.g. File > Save, or export to a new .bin path). Note
   the exact output path.
5. Test that this manually-edited bin actually shows the "want to save?"
   prompt when going D1→D2, to confirm it's a known-good reference.

### Step 3 — dump and compare

Run the dump script against your manually-edited bin and paste the full
output back here:

```
python3 mods/single-disc/scripts/dump_blackbgb_debug.py path/to/your-manual-edit.bin
```

Also run it against the latest auto-built bin for comparison:

```
python3 mods/single-disc/scripts/dump_blackbgb_debug.py workspace/iso-extract/single-disc-dskcg-tablefix-test.bin
```

Paste both full outputs (or the exact file paths used) so the two
"init slot 0" script dumps can be diffed byte-for-byte.

---

script output

python3 mods/single-disc/scripts/build_work_bin.py -o workspace/iso-extract/single-disc-dskcg-tablefix-test.bin

Loading CSR D1/D2 reference images...
Base: CSR D1 (747,435,024 bytes)

Applying 8-field rework merge (verdict table)...
  [slot-splice] BUGIN1A: 1 slots spliced, new size 12195 bytes
  [slot-splice] NIVGATE: 13 slots spliced, new size 7213 bytes
  [slot-splice] RCKTIN2: 1 slots spliced, new size 17822 bytes

Applying bulk safe-field merge (non-collision D2/D3 edits)...
  Applied 67/67 safe field merges

Removing DSKCG (ask-for-disc) ops via live splicer for ['BLACKBGB'] (only occurrence(s) [3])...
    init slot 0: Removed 1 DSKCG
  BLACKBGB: removed 1 DSKCG (12929 bytes)
  Total fields modified: 1

Patching FIELD.BIN/WORLD.BIN embedded (location,size) tables...
  FIELD/FIELD.BIN table: BLACKBGB.DAT @58550 size 13013 -> 12929
  FIELD/FIELD.BIN table: BLIN66_6.DAT @72265 size 13316 -> 13340
  FIELD/FIELD.BIN table: BLIN70_4.DAT @73653 size 9579 -> 9595
  FIELD/FIELD.BIN table: BUGIN1A.DAT @100193 size 12117 -> 12195
  FIELD/FIELD.BIN table: CANON_2.DAT @121844 size 24844 -> 24698
  FIELD/FIELD.BIN table: CONDOR2.DAT @81722 size 7211 -> 7217
  FIELD/FIELD.BIN table: CONVIL_1.DAT @81793 size 24285 -> 24306
  FIELD/FIELD.BIN table: CONVIL_2.DAT @81936 size 21290 -> 21156
  FIELD/FIELD.BIN table: CRATER_1.DAT @117071 size 12314 -> 12320
  FIELD/FIELD.BIN table: CRATER_2.DAT @117223 size 18114 -> 18129
  FIELD/FIELD.BIN table: FR_E.DAT @80996 size 16368 -> 16376
  FIELD/FIELD.BIN table: FSHIP_1.DAT @55277 size 4926 -> 4911
  FIELD/FIELD.BIN table: FSHIP_22.DAT @55605 size 12093 -> 12097
  FIELD/FIELD.BIN table: FSHIP_23.DAT @55782 size 21390 -> 21387
  FIELD/FIELD.BIN table: FSHIP_24.DAT @55957 size 15572 -> 15617
  FIELD/FIELD.BIN table: FSHIP_25.DAT @56136 size 29850 -> 29800
  FIELD/FIELD.BIN table: FSHIP_3.DAT @56317 size 12071 -> 12074
  FIELD/FIELD.BIN table: FSHIP_4.DAT @56425 size 17328 -> 17293
  FIELD/FIELD.BIN table: GAIA_32.DAT @116589 size 5535 -> 5536
  FIELD/FIELD.BIN table: GAIIN_6.DAT @116885 size 9541 -> 9542
  FIELD/FIELD.BIN table: HYOU7.DAT @114422 size 15007 -> 15059
  FIELD/FIELD.BIN table: ITHOS.DAT @119756 size 16171 -> 16187
  FIELD/FIELD.BIN table: ITOWN1A.DAT @118600 size 22854 -> 22856
  FIELD/FIELD.BIN table: ITOWN2.DAT @119255 size 8658 -> 8627
  FIELD/FIELD.BIN table: ITOWN_W.DAT @119465 size 12027 -> 12000
  FIELD/FIELD.BIN table: JUNAIR.DAT @84555 size 26248 -> 26279
  FIELD/FIELD.BIN table: JUNBIN22.DAT @85651 size 12917 -> 12923
  FIELD/FIELD.BIN table: JUNBIN3.DAT @85725 size 11491 -> 11506
  FIELD/FIELD.BIN table: JUNBIN4.DAT @85785 size 18015 -> 17963
  FIELD/FIELD.BIN table: JUNBIN5.DAT @85889 size 17912 -> 17894
  FIELD/FIELD.BIN table: JUNIN2.DAT @84980 size 17990 -> 17997
  FIELD/FIELD.BIN table: JUNONE2.DAT @86715 size 11095 -> 11094
  FIELD/FIELD.BIN table: JUNONE22.DAT @125702 size 5921 -> 5929
  FIELD/FIELD.BIN table: JUNONE7.DAT @87142 size 12269 -> 12210
  FIELD/FIELD.BIN table: LAS4_0.DAT @124908 size 15377 -> 15395
  FIELD/FIELD.BIN table: LAS4_2.DAT @125223 size 6879 -> 6880
  FIELD/FIELD.BIN table: LAS4_4.DAT @125283 size 6325 -> 6334
  FIELD/FIELD.BIN table: LASTMAP.DAT @125347 size 23302 -> 23326
  FIELD/FIELD.BIN table: LOSLAKE1.DAT @109793 size 21195 -> 21207
  FIELD/FIELD.BIN table: LOST2.DAT @109345 size 16974 -> 17032
  FIELD/FIELD.BIN table: MD8BRDG2.DAT @121560 size 17846 -> 17695
  FIELD/FIELD.BIN table: MD8_6.DAT @121053 size 19843 -> 19695
  FIELD/FIELD.BIN table: MTCRL_2.DAT @92237 size 23601 -> 23436
  FIELD/FIELD.BIN table: NIVGATE.DAT @74319 size 7378 -> 7213
  FIELD/FIELD.BIN table: NIVGATE2.DAT @74381 size 7308 -> 7280
  FIELD/FIELD.BIN table: NIVL_B22.DAT @75913 size 16492 -> 16400
  FIELD/FIELD.BIN table: RCKTBAS1.DAT @102419 size 26218 -> 26193
  FIELD/FIELD.BIN table: RCKTBAS2.DAT @102591 size 24129 -> 24100
  FIELD/FIELD.BIN table: RCKTIN2.DAT @102803 size 17713 -> 17822
  FIELD/FIELD.BIN table: RCKTIN3.DAT @102897 size 13328 -> 13335
  FIELD/FIELD.BIN table: RCKTIN5.DAT @103028 size 20893 -> 20923
  FIELD/FIELD.BIN table: RCKTIN6.DAT @103111 size 16186 -> 16172
  FIELD/FIELD.BIN table: RCKTIN7.DAT @103210 size 13186 -> 13202
  FIELD/FIELD.BIN table: SEMKIN_4.DAT @87948 size 22539 -> 22373
  FIELD/FIELD.BIN table: SEMKIN_5.DAT @88116 size 22225 -> 22069
  FIELD/FIELD.BIN table: SUBIN_1B.DAT @86260 size 19932 -> 19963
  FIELD/FIELD.BIN table: TRNAD_1.DAT @117324 size 15788 -> 15796
  FIELD/FIELD.BIN table: TRNAD_2.DAT @117485 size 13054 -> 13069
  FIELD/FIELD.BIN table: TRNAD_4.DAT @117727 size 19219 -> 19195
  FIELD/FIELD.BIN table: TRNAD_51.DAT @117880 size 15250 -> 15248
  FIELD/FIELD.BIN table: TRNAD_52.DAT @118054 size 6374 -> 6425
  FIELD/FIELD.BIN table: TUNNEL_6.DAT @126016 size 23251 -> 23082
  FIELD/FIELD.BIN table: WHITE1.DAT @110379 size 11459 -> 11472
  FIELD/FIELD.BIN table: WHITE2.DAT @110479 size 9395 -> 9381
  FIELD/FIELD.BIN table: ZCOAL_1.DAT @120619 size 16023 -> 15851
  FIELD/FIELD.BIN table: ZCOAL_3.DAT @120814 size 15161 -> 14989
  FIELD/FIELD.BIN table: ZMIND1.DAT @120288 size 9323 -> 9246
  FIELD/FIELD.BIN table: ZMIND2.DAT @120402 size 9266 -> 9285
  FIELD/FIELD.BIN table: ZMIND3.DAT @120498 size 12123 -> 12163
Source (dec):     C:\Users\David\AppData\Local\Temp\tmpheyxov7m\bin.dec (264008 bytes)
Original (bin):   C:\Users\David\AppData\Local\Temp\tmpheyxov7m\bin.orig (85346 bytes)
Output:           C:\Users\David\AppData\Local\Temp\tmpheyxov7m\bin.new (81162 bytes)
Method:           zopfli
Size delta:       -4184 bytes
Shorter than original — CDmage 'pad with zeros?' → Yes.
  Total table entries patched: 69

Wrote workspace\iso-extract\single-disc-dskcg-tablefix-test.bin (747,435,024 bytes) [pre-SNOVA]

Injecting SNOVA D3 -> D1...
D3 SNOVA raw block LBA 127100+570 files=17
grow sectors 317787 -> 318357 (delta LBA 190687)
patch BATTLE.X hardcoded SNOVA LBAs (delta 190687)
  BATTLE.X LBA 0x48D78: 127254 -> 317941
  BATTLE.X LBA 0x48D80: 127293 -> 317980
  BATTLE.X LBA 0x48D88: 127320 -> 318007
  BATTLE.X LBA 0x48D90: 127354 -> 318041
  BATTLE.X LBA 0x48D98: 127373 -> 318060
  BATTLE.X LBA 0x48DA0: 127394 -> 318081
  BATTLE.X LBA 0x48DA8: 127430 -> 318117
  BATTLE.X LBA 0x48DB0: 127442 -> 318129
  BATTLE.X LBA 0x48DB8: 127464 -> 318151
  BATTLE.X LBA 0x48DC0: 127503 -> 318190
  BATTLE.X LBA 0x48DC8: 127544 -> 318231
  BATTLE.X LBA 0x48DD0: 127555 -> 318242
  BATTLE.X LBA 0x48DD8: 127562 -> 318249
  BATTLE.X LBA 0x48DE0: 127571 -> 318258
  BATTLE.X LBA 0x48DE8: 127618 -> 318305
  BATTLE.X LBA 0x48DF0: 127649 -> 318336
  BATTLE.X LBA 0x4F5A8: 127101 -> 317788
Source (dec):     C:\Users\David\AppData\Local\Temp\tmpe1q2qnkq\BATTLE.X.dec (342188 bytes)
Original (bin):   C:\Users\David\AppData\Local\Temp\tmpe1q2qnkq\BATTLE.X.orig (130322 bytes)
Output:           C:\Users\David\AppData\Local\Temp\tmpe1q2qnkq\BATTLE.X.new (123557 bytes)
Method:           zopfli
Size delta:       -6765 bytes
Shorter than original — CDmage 'pad with zeros?' → Yes.
  BATTLE.X recompress 130322 -> 123557 (pad 6765)
wrote workspace\iso-extract\single-disc-dskcg-tablefix-test.bin (raw-copy + BATTLE.X LBA patch v3)
verify: BATTLE.X 17 LBA entries remapped
verify: all SNOVA files match D3

Done. Final work bin: workspace\iso-extract\single-disc-dskcg-tablefix-test.bin


# Task: Test D1->D2 transition with DSKCG removal + FIELD.BIN table fix

## Why

Root cause found: it was never the jump-fixup math (independently
verified byte-for-byte correct — every JMPF/IFUB target in the patched
BLACKBGB script lands exactly on an instruction boundary, 0 bad
jumps). The real bug is in the pipeline step *after* DSKCG removal.

FIELD.BIN has its **own embedded `(LBA, size)` lookup table**,
separate from the ISO9660 directory record that
`replace_file_within_sectors()` patches. Removing a DSKCG opcode
shrinks BLACKBGB's compressed size, so the ISO9660 dirent gets the
correct new size — but FIELD.BIN's internal table still points at the
field's **old pre-edit size**. `fix_field_bin_table.py` (which patches
that internal table) existed but was gated behind an opt-in
`--apply-table-fix` flag that `build_work_bin.py` did **not** pass by
default. So every build you tested had a stale FIELD.BIN table entry
for BLACKBGB, which is exactly consistent with what you saw: the game
loads BLACKBGB at the wrong byte length (truncating before the ASK/
save-prompt opcode) → black screen, no save prompt. It also explains
Makou's "Invalid Archive": Makou's own `updateBin()` searches FIELD.BIN
for `(LBA, old_size)` to relocate the field on save and fails to find
it once the size no longer matches.

Fix: `--apply-table-fix` is now the **default** behavior (renamed to
an opt-out `--skip-table-fix` debug flag). `build_work_bin.py` always
patches FIELD.BIN/WORLD.BIN's internal tables after any field-resizing
step, so BLACKBGB's real new size and the table's record of it always
agree.

DSKCG removal itself still only strips occurrence index 3 (script
offset 518 in BLACKBGB's `init` slot 0, gated by
`if var[3][136] bitON 4`) — confirmed as the one on the actual D1->D2
execution path.

## Prerequisites

- `workspace/pristine/FINALFANTASY7_D1.bin`, `_D2.bin`, `_D3.bin` present.
- `Final-Fantasy-7-CSR` repo checked out as a sibling of this repo.
- Python 3 on PATH; run all commands from this repo's root.

## What you do

1. `git pull --ff-only`.
2. Rebuild the work bin and a matching `.cue`:

   ```bash
   python3 mods/single-disc/scripts/build_work_bin.py -o workspace/iso-extract/single-disc-dskcg-tablefix-test.bin
   printf 'FILE "single-disc-dskcg-tablefix-test.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > workspace/iso-extract/single-disc-dskcg-tablefix-test.cue
   ```

   Expect this line during the DSKCG-removal step:
   ```
   Removing DSKCG (ask-for-disc) ops via live splicer for ['BLACKBGB'] (only occurrence(s) [3])...
       init slot 0: Removed 1 DSKCG
   ```
   and later, during the table-fix step (no longer skipped):
   ```
   Patching FIELD.BIN/WORLD.BIN embedded (location,size) tables...
     FIELD/FIELD.BIN table: BLACKBGB.DAT @... size ... -> ...
   ```
   No `WARNING:` or uncaught errors.

3. Open `workspace/iso-extract/single-disc-dskcg-tablefix-test.cue` in
   DuckStation fresh (no save states, no cheats).
4. New game, play through Midgar to confirm baseline sanity (no hangs).
5. Progress to the Disc 1->2 transition (BLACKBGB field #103 -> LOST2
   -> break scene -> COS_BTM2). Confirm it goes straight through with
   no black-screen hang, and that the disc-swap **save prompt** (ASK
   opcode) still appears normally on that path.
6. Open this bin in Makou Reactor and check BLACKBGB field #103.
   Confirm it opens cleanly (no "Invalid Archive"), and that the
   script displays with clean "Goto label X" jumps (no "Forward N
   byte(s)" raw offsets). Try File > Save to confirm Makou can save
   the archive without error.

## Evidence (paste)

```
D1->2 transition with DSKCG removal + table fix: NO HANG / HANGS
Save prompt (ASK) appears on that path: YES / NO
Makou Reactor BLACKBGB open: OK / Invalid Archive
Makou Reactor save: OK / error (describe)
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
