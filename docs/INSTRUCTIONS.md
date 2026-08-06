# Task: playtest ending credits on oversize D1 bin

## Why

Disc 3 ending streams were missing on single-disc D1 (wrong short clip, then black).
For a **DuckStation test** we put D3 endings into the same **movie table ids** Disc 3 uses.

| MOVIE_ID id | Disc 3 file | Put on D1 over |
|------------:|-------------|----------------|
| 25 | ENDING01.MOV | SMK.STR |
| 26 | ENDING3E.MOV | SOUTHMK.MOV |
| 29 | ENDING2E.MOV | MONITOR.STR |

Payload matches Disc 3. Image is **~1008 MB** (not burnable as 80‑min CD).

## What you do

1. Pull  
2. Open the ending-test cue (rebuild only if the bin is missing)  
3. Run past final battle / credits  
4. Reply what you saw  

---

## 0. Update

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only
```

---

## 1. Open the test image (if already built on this machine)

```text
workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

Expect bin about **1008274176** bytes (~962 MiB).

**Do not** use `ff7_d1_playtest_csr_sd_movies.cue` for this test (no endings).

---

## 2. Rebuild ending-test bin if needed

```bash
cd /path/to/Final-Fantasy-7-Modding

python3 mods/single-disc/scripts/build_playtest_bin.py

cp -f workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.bin \
      workspace/iso-extract/ff7_d1_playtest_ending_test.bin

python3 mods/single-disc/scripts/inject_movies_by_disc_id.py \
  --d1 workspace/iso-extract/ff7_d1_playtest_ending_test.bin \
  --manifest mods/single-disc/patches/ending-credits-test-manifest.txt \
  --in-place

printf '%s\n' \
  'FILE "ff7_d1_playtest_ending_test.bin" BINARY' \
  '  TRACK 01 MODE2/2352' \
  '    INDEX 01 00:00:00' \
  > workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

---

## 3. Smoke

- Load a save just before / after final battle if you have one  
- Credits path should play real ending video + audio (not random short FMV / dead black)  
- Note: anything else that used movie ids 25/26/29 on D1 will now show ending footage  

---

## 4. Reply

1. Bin size on disk  
2. What played after the final fight  
3. Any audio/video glitch  

## Notes

- This is **not** shipped in the builder pack (too big for CD).  
- Finding: `docs/findings/2026-08-07-ending-credits-test-inject.md`  
- CD-sized credits still need reclaiming other movies or a field stub later.  
