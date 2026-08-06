# Task: ending credits test v2 (scripts + streams)

## Why the last test failed

Only swapping movie **files** was not enough.

- Single-disc **LASTMAP** had the ending **Play movie** removed.
- Single-disc **LAS4_0** jumped over the ending movie set/play.
- So the game never drove the D3 ending streams correctly → random clip / black silence.

## What we fixed (local test bin)

1. Restored **pristine** `LASTMAP.DAT` and `LAS4_0.DAT` (movies play again).
2. Injected Disc 3 streams into the **MOVIE_ID** rows Disc 3 uses (23–26, 29).

| Table id | Disc 3 file |
|---------:|-------------|
| 23 | LASTMAP.BIN |
| 24 | LASTFLOR.MOV |
| 25 | ENDING01.MOV |
| 26 | ENDING3E.MOV |
| 29 | ENDING2E.MOV |

Image is still **~1.0 GB** (DuckStation only).

## What you do

1. Pull  
2. Open the ending-test cue (rebuild if missing)  
3. Run past final battle into credits  
4. Reply what you saw  

---

## 0. Update

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only
```

---

## 1. Open test image

```text
workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

Expect bin size **1008274176**.

Do **not** use `ff7_d1_playtest_csr_sd_movies.cue` for this test.

---

## 2. Rebuild if the bin is missing

```bash
cd /path/to/Final-Fantasy-7-Modding

python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
```

(If that script is not present yet, use the steps in  
`docs/findings/2026-08-07-ending-credits-test-inject.md`.)

---

## 3. Smoke

After final battle / northern cave last maps:

- Should set and play real ending streams (not a random short Midgar clip)
- Audio should be present on the long credits if ENDING2E runs
- Note any black gap or wrong short FMV  

---

## 4. Reply

1. Bin size  
2. What played after the final fight  
3. Sound yes/no  
