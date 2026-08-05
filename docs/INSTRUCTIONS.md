# Task: build playtest .bin (CSR + single-disc + movies)

**One command** (preferred). Writes the only bin you should open in DuckStation.

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only
git -C ../Final-Fantasy-7-CSR pull --ff-only

python3 mods/single-disc/scripts/build_playtest_bin.py
```

Output (must both exist):

    workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.bin   # ~731 MB / 766084032 bytes
    workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.cue

Open the **.cue** in DuckStation.

The script **fails** unless MOVIE/JAIROFAL.MOV is byte-identical to D2 CANONON.MOV.

## Critical: do not open the wrong .bin

workspace/iso-extract/ has many old work bins (~714 MB). Those are often **core-only**
(no movies) and will play pristine D1 jairofal / rocket standing on launch pad at LOSLAKE1 (#637).

| File | Approx size | #637 movie |
|------|-------------|------------|
| *_core_*.bin / playtest_work.bin / noswap work | ~714 MB | vanilla jairofal (wrong for manip) |
| **ff7_d1_playtest_csr_sd_movies.bin** | **~731 MB (766084032)** | **CANONON (correct)** |

If the file you open is not ~731 MB, you are not testing movies.

## Why pristine D1 matches the rocket/jairo clip

Retail: PMVIE id 47 is jairofal on D1 and canonon on D2. Single-disc uses disc-1 rules.
Only the manip-movies layer replaces JAIROFAL data with CANONON + patches MOVIE_ID.

## Manual three-step (same as the script)

```bash
PRISTINE=workspace/pristine/FINALFANTASY7_D1.bin
CSR_LAYER=../Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json
CORE_LAYER=builder/single-disc-on-csr-v0.1.1/layers/disc1.layer.json
MOVIE_LAYER=builder/single-disc-csr-manip-movies-v0.1.0/layers/disc1.layer.json
OUT=workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.bin
python3 scripts/apply_layer.py "$PRISTINE" "$CSR_LAYER" -o workspace/iso-extract/ff7_d1_csr_base_local.bin
python3 scripts/apply_layer.py workspace/iso-extract/ff7_d1_csr_base_local.bin "$CORE_LAYER" -o workspace/iso-extract/ff7_d1_csr_sd_core_local.bin
python3 scripts/apply_layer.py workspace/iso-extract/ff7_d1_csr_sd_core_local.bin "$MOVIE_LAYER" -o "$OUT"
```

---


# DuckStation — LOSLAKE1 (#637) — DO THIS

Bin must be **766084032** bytes. Open only:

    workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.cue

Rebuild if needed:

```bash
git pull --ff-only
python3 mods/single-disc/scripts/build_playtest_bin.py
```

## Known (done)

- Script (Makou): **Set next movie jairofal/canonon/No47** then Play — id **47**
- Host pack: JAIROFAL slot = CANONON @ LBA **318357**
- BP `0x800CCE94` is correct; `800722C4` is **not** movie id

## DO NOW (paused on bad FMV at 0x800CCE94)

### 1. Memory goto `8009C6E0`

- Screenshot 16 bytes
- Write the 4-byte LE pointer **P** (first 4 bytes)

### 2. Memory goto **P**

- Screenshot 16 bytes
- Movie id = bytes at **P+2** and **P+3** (LE u16)
  - `2F 00` = 47
  - `2D 00` = 45

### 3. Memory Search (LE hex) — which hits?

| Bytes | LBA | Stream |
|-------|----:|--------|
| `95 DB 04 00` | 318357 | CANONON (pack) |
| `51 F1 03 00` | 258385 | vanilla jairofal |
| `BB BE 03 00` | 245435 | rcktfail |

### 4. Send back

Only these:

1. P (from step 1)
2. 16 bytes at P (step 2)
3. Which search row(s) hit (step 3)
4. Screenshot of game FMV if easy

Do **not** re-dump 8009D820 / 800722C4 / 800716CC.
