# Your turn: manip-movies playtest (credits on CD is next track)

## Product

- **Credits on CD** — yes (ending LBA builder keeps streams; no field unskip).
- **Now** — playtest **manip-movies** on the normal stack.

## Build / open (manip playtest)

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only
python3 mods/single-disc/scripts/build_playtest_bin.py
```

Open in DuckStation:

```text
workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.cue
```

Expect ~731 MiB class size; builder fails if CANONON seed or LBA 250450 Form2 is wrong.

## Check (manip)

| Scene | Expect |
|-------|--------|
| LOSLAKE1 lake | CANONON video+audio (seek 250450) |
| CANON_2 / Hojo path | CANONHT2 still usable |
| Any path needing LAST4_3 / LASTMAP.BIN bodies | seed slots (GOLD7_2 / JAIROFLY) |

Do **not** treat CSR/SD skipped Plays (e.g. LAS4_0 ENDING01 JMPF) as failures.

Paste DuckStation notes / OK-fail. Push if you drop logs in-repo.

## Credits CD (after manip OK)

```bash
python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
# workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

- Keeps CSR/SD fields (no pristine LAS4_0).
- Puts ending streams at D3 LBAs; re-punches CANONON@250450 + LAST4_3.
- Mid-ENDING2E may glitch where CANONON sits (lake priority).

## Builder change (this commit)

`build_ending_credits_test_bin.py` no longer overwrites LAS4_0/LASTMAP.
