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


---

# DuckStation debugger — LOSLAKE1 wrong FMV (#637)

Use this when the local playtest bin still shows the rocket/launch-pad clip.
Goal: capture movie id and which ISO LBA is read when the bad FMV starts.

## 0. Only debug the movies playtest bin

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only
python3 mods/single-disc/scripts/build_playtest_bin.py
ls -lh workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.bin
```

Must be **766084032 bytes** (~731 MB). If ~714 MB, movies were not applied — stop.

Open in DuckStation:

    workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.cue

Do **not** open other workspace/iso-extract/ff7_d1_*.bin files.

Host-side LBA check (optional):

```bash
python3 -c '
from pathlib import Path
import sys
sys.path.insert(0, "scripts")
from psx_mode2_iso import find_file
b = Path("workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.bin").read_bytes()
print("JAIROFAL", find_file(b, "MOVIE/JAIROFAL.MOV"))
print("RCKTFAIL", find_file(b, "MOVIE/RCKTFAIL.MOV"))
'
```

On current packs expect JAIROFAL **LBA=318357 size=15071232** (CANONON body).
Vanilla jairofal LBA was **258385**. RCKTFAIL is **245435**.

## 1. DuckStation setup

1. Enable debugger (Settings / Tools — Enable debugging).
2. Boot the playtest **.cue** above.
3. Reach LOSLAKE1 (#637). Pause **as the wrong FMV starts** (frame-advance helps).

## 2. Breakpoint — Play movie handler

FIELD load base **0x800A0000**. MOVIE opcode handler entry:

```text
CPU Execute breakpoint: 0x800CCE94
```

When it hits during the bad cutscene, dump the memory below.

Related known addrs (from field movie RE):

| Addr | Role |
|------|------|
| 0x800CCE94 | MOVIE (0xF9) handler entry |
| 0x800722C4 | u8 field index (script entity index area) |
| 0x80071C1C | flag cleared in abandoned movie stubs |
| 0x801144D4 | related flag |

## 3. Memory to dump (screenshot or hex paste)

While FMV is playing / at breakpoint:

### 3a. Small RAM dumps

```text
0x800722C0  length 32 bytes
0x80071C00  length 64 bytes
0x801144D0  length 16 bytes
```

Note especially **u8 at 0x800722C4**.

### 3b. Best signal — ISO LBA being read

If DuckStation can log CD/ISO reads or break on sector read, note the **LBA** when the pad FMV starts:

| LBA (playtest pack) | Meaning |
|--------------------:|---------|
| **318357** | CANONON stream (pack installed; inject path OK) |
| **258385** | Vanilla JAIROFAL (old slot — wrong bin or MOVIE_ID not used) |
| **245435** | RCKTFAIL (rocket pad family — likely PMVIE id 45, not 47) |
| other | paste the number |

### 3c. Host confirm open file

```bash
ls -lh workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.bin
# must show 766084032 (or matching current pack size)
```

## 4. Makou cross-check (same scene)

On the **same** playtest .bin in Makou:

1. Field **loslake1** / #637
2. Find the **Play movie** that matches what you see
3. Note full **Set next movie** line and **id** (e.g. 47 jairofal/canonon vs 45 rcktfail)

Makou list order is **engine id**, not ISO A-Z. Disc 1 examples:

| Id | Disc 1 name |
|---:|-------------|
| 45 | rcktfail |
| 46 | jairofly |
| 47 | jairofal |
| 48 | gold7 |
| ... | ... |
| 54+ | No54, No55, ... |

Id **47** on D1 = jairofal; on D2 = canonon (same PMVIE byte).

## 5. What to send back

1. Full path of .bin/.cue DuckStation opened
2. Size of that .bin
3. u8 **0x800722C4** (and dump 0x800722C0-0x800722DF)
4. Movie **LBA read** if available (318357 / 258385 / 245435 / other)
5. Makou Set next movie line + id for that Play

## 6. How we interpret

| Result | Meaning |
|--------|---------|
| LBA 318357, still looks wrong | Content/scene mismatch; id may still be wrong scene |
| LBA 258385 | Still vanilla jairofal — wrong image or MOVIE_ID not applied |
| LBA 245435 | Playing **rcktfail (id 45)** — different fix than id 47 CANONON |
| Bin size ~714MB | Core-only build; rerun build_playtest_bin.py |


# Windows disk cleanup (Git Bash) — low free space can break Makou

Makou ISO save writes a full-size temp (`*.makoutemp`, ~0.7 GB for D1) next to the
work `.bin`. If **C:** (or the drive holding the bin / `%TEMP%`) is nearly full,
save can fail with **invalid archive** even when the script edit is fine.

Use **Git Bash** below. Paths are typical Windows; adjust if your drive letter
or user name differs.

## Free space

```bash
# C: free/used (Git Bash)
df -h /c/

# TEMP location (Makou/OS temp often lands here)
echo "TEMP=$TEMP"
echo "TMP=$TMP"
df -h "$TEMP" 2>/dev/null || df -h /c/Users/"$USER"/AppData/Local/Temp
```

Aim for several free GB on the drive where the `.bin` lives and on TEMP.

## Largest top-level dirs on C:

```bash
# Slow but useful overview (may need a minute)
du -h -d 1 /c/ 2>/dev/null | sort -hr | head -25
```

## Common hogs (faster)

```bash
du -h -d 0 \
  /c/Users \
  /c/Users/"$USER" \
  /c/Users/"$USER"/AppData/Local \
  /c/Users/"$USER"/AppData/Roaming \
  /c/Users/"$USER"/Downloads \
  /c/Windows/Temp \
  /c/Users/"$USER"/AppData/Local/Temp \
  "/c/Program Files" \
  "/c/Program Files (x86)" \
  2>/dev/null | sort -hr
```

## Largest files under your profile (>200 MB)

```bash
find /c/Users/"$USER" -type f -size +200M 2>/dev/null \
  -printf '%s\t%p\n' | sort -nr | head -40 | awk '{printf "%.2f GB\t%s\n", $1/1024/1024/1024, $2}'
```

## FF7 / project bins and builder leftovers

```bash
# Adjust roots to your clone locations
find /c/Users/"$USER" /d/projects /c/projects \
  \( -name '*.bin' -o -name '*.iso' -o -name '*.img' -o -name '*.makoutemp' -o -name '*.zip' \) \
  -type f 2>/dev/null -printf '%s\t%p\n' | sort -nr | head -40 \
  | awk '{printf "%.2f GB\t%s\n", $1/1024/1024/1024, $2}'
```

## Repo workspace junk (safe candidates after you are done testing)

From a Modding clone (example):

```bash
cd /d/projects/Final-Fantasy-7-Modding   # or your path

# Work bins (gitignored) — each ~0.7 GB
du -h workspace/iso-extract/*.bin 2>/dev/null | sort -hr

# List only; delete what you do not need (keep pristine/)
ls -lh workspace/iso-extract/*.bin 2>/dev/null
ls -lh workspace/pristine/ 2>/dev/null
```

Do **not** delete `workspace/pristine/FINALFANTASY7_D*.bin` (retail masters).

Optional cleanup examples (only if you are sure):

```bash
# Old playtest / work bins (examples — edit names first)
# rm -f workspace/iso-extract/ff7_d1_*_work.bin
# rm -f workspace/iso-extract/ff7_d1_*_playtest*.bin

# Makou leftover temps next to a bin
# find workspace -name '*.makoutemp' -ls
# rm -f workspace/iso-extract/*.makoutemp

# User TEMP (closes apps using temp first)
# rm -rf /c/Users/"$USER"/AppData/Local/Temp/*
```

## PowerShell alternatives (if preferred)

```powershell
Get-PSDrive C | Format-List Used,Free
Get-ChildItem $env:USERPROFILE -Recurse -File -Force -ErrorAction SilentlyContinue |
  Where-Object { $_.Length -gt 200MB } |
  Sort-Object Length -Descending |
  Select-Object -First 40 @{N='GB';E={[math]::Round($_.Length/1GB,2)}}, FullName
```

## After cleanup

1. Confirm `df -h /c/` shows comfortable free space.
2. Prefer Makou on a **fresh** CSR+pack apply bin, not a pile of old grown copies.
3. New builder zip from pristine D1 when testing published packs.
