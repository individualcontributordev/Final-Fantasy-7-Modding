# Task: burn CD-sized ending credits image

## Size (already CD-safe)

Verified layout does **not** grow the image past an 80-min disc:

| | |
|--|--|
| Bin size | **766340400** bytes (~**730.8 MiB**) |
| Sectors | **325825** |
| 80-min budget | 360000 sectors (~807 MiB) |
| Free | **~34175** sectors (~**76.7 MiB**) |

"Reclaim" is not shrinking further — v6 already fits. Endings sit at Disc 3
LBAs **inside** the existing image (no ~200 MiB EOF append).

## Build (local only — not a builder pack)

Delta ~200 MiB raw → layer JSON would blow GitHub 100 MB. Build on a machine
with pristine D1–D3:

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only
python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
```

Open / burn:

```text
workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

**MODE2/2352** raw from the .cue (ImgBurn / CDRWIN style).

## What the build does

1. CSR + single-disc core + manip-movies **0.1.2**
2. LASTMAP v5 (no early MDEC MOVIE) + pristine LAS4_0
3. alias_d3_ending_lbas_on_d1.py — D3 streams at **D3 LBAs**

| id | Stream | LBA |
|---:|--------|----:|
| 23 | LASTMAP.BIN | 161972 |
| 24 | LASTFLOR.MOV | 162081 |
| 25 | ENDING01.MOV | 163608 |
| 26 | ENDING3E.MOV | 172631 |
| 29 | ENDING2E.MOV | 197242 |

## Tradeoffs on this burn

- Overwrites mid-disc D1 movies under those LBA ranges.
- **ENDING2E includes LBA 250450** → stomps **CANONON / LOSLAKE1** absolute
  seek (DS log: setloc 55:41:25 = 250450). Credits stay continuous;
  lake FMV may glitch. Not in CDN/builder packs yet.

## Smoke

1. Bin size **766340400**
2. LASTMAP / post-final → ending FMV + audio
3. Optional: note LOSLAKE1

## Reply

Burn OK? endings OK on disc? anything broken mid-game?
