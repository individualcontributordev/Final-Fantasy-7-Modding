# Task: build playtest .bin (CSR + single-disc + movies)

**One command** (preferred). Writes the only bin you should open in DuckStation.

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only
git -C ../Final-Fantasy-7-CSR pull --ff-only

python3 mods/single-disc/scripts/build_playtest_bin.py
```

Output (must both exist):

    workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.bin   # ~731 MB / ~766340400 bytes (v0.1.1)
    workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.cue

Open the **.cue** in DuckStation.

The script **fails** unless MOVIE/JAIROFAL.MOV is byte-identical to D2 CANONON.MOV
and ISO LBA 250450 starts with CANONON (D2-style seek alias).

## Critical: do not open the wrong .bin

workspace/iso-extract/ has many old work bins (~714 MB). Those are often **core-only**
(no movies) and will play pristine D1 jairofal / rocket standing on launch pad at LOSLAKE1 (#637).

| File | Approx size | #637 movie |
|------|-------------|------------|
| *_core_*.bin / playtest_work.bin / noswap work | ~714 MB | vanilla jairofal (wrong for manip) |
| **ff7_d1_playtest_csr_sd_movies.bin** | **~731 MB (~766340400 v0.1.1)** | **CANONON + LBA250450 alias** |

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


# LOSLAKE1 (#637) — FIX in pack v0.1.1

Logs: `docs/logs single disc 1.txt`, `docs/logs real disc 2.txt`
Finding: `docs/findings/2026-08-05-loslake1-cdrom-d1-vs-d2.md`

**Root cause:** both discs CD-seek ISO **LBA 250450** (DS sector 250600).
D2 = CANONON start. Old D1 pack = mid-RCKTFAIL (rocket). MOVIE_ID[47] was already correct; player did not use it.

**Fix (single-disc-csr-manip-movies-v0.1.1):**
- Still CANONON → JAIROFAL + MOVIE_ID[47]
- **Also** raw-copy CANONON Form2 sectors at LBA **250450** (D2 seek target; not 2048-only)
- Relocate JAIROFLY/LASTMAP off that range

## Playtest now

```bash
git pull --ff-only
python3 mods/single-disc/scripts/build_playtest_bin.py
```

Open `workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.cue` only.
Expect bin size **~766340400** (slightly larger than 766084032).

LOSLAKE1 FMV should match real D2 (CANONON), not rocket pad.

Optional CD log check: long stream starts DS **250600** and stays on CANONON-length read (~6697 sectors), not 1529 mid-RCKTFAIL.

**Tradeoff:** tail of RCKTFAIL.MOV on D1 is overwritten by the alias.

---


## Next manip-movies candidates (after LOSLAKE1)

Headroom ~77 MB raw on current playtest bin (80-min CD).

| Priority | Movie | Disc | MB | Notes |
|---------:|-------|:----:|---:|-------|
| 1 | LOSLAKE1.MOV + LSLMV.STR | D2 | ~7.5 | ioslake3 Bugenhagen; or trim Set+Play |
| 2 | CANONHT2 playtest | D2 | (seeded) | Hojo CANON_2 — confirm stream |
| 3 | LAST* endgame stubs | D3 | (seeded) | LAST4_3/LASTMAP on GOLD7_2/JAIROFLY |
| 4 | PHOENIX.MOV | D2 | ~8.3 | BLIN70_4 if CSR still plays |
| - | LASTFLOR.MOV | D3 | ~3 | deferred — id clash with CANONON/JAIROFAL |

Rebuild playtest:

    git pull --ff-only
    python3 mods/single-disc/scripts/build_playtest_bin.py

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


logs








































































































































































