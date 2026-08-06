# Task: ending credits test v3 (Form2 MOVIE_ID sizes)

## Why LASTMAP froze on v2

Field scripts and D3 movie **bytes** were already on the image, but
`MOVIE_ID.BIN` **size** was set to the ISO file length (2048×sectors).

The movie player needs Disc 3’s lengths: usually **2336×sectors**, plus the
same extra fields Disc 3 stores for that stream. Wrong length → freeze on play.

## What we fixed (local test bin)

1. Pristine `LASTMAP.DAT` / `LAS4_0.DAT` (ending Play movie ops).
2. D3 streams on table ids **23, 24, 25, 26, 29**.
3. **MOVIE_ID** size + aux copied from Disc 3; only the **LBA** is ours (grew).

Still **~1.0 GB** — DuckStation only, not a real CD.

## What you do

1. Pull  
2. Open ending-test cue (rebuild if missing/old)  
3. Run past final battle / LASTMAP into credits  
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

## 2. Rebuild if needed

```bash
cd /path/to/Final-Fantasy-7-Modding

python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
```

---

## 3. Smoke

On LASTMAP and after final battle:

- Should **not** freeze on the first ending movie
- Real ending / credits streams, with sound on the long credit roll if it runs
- Note any freeze, black gap, or wrong short FMV  

---

## 4. Reply

1. Bin size  
2. What played on LASTMAP / after final fight  
3. Sound yes/no / freeze yes-no  
