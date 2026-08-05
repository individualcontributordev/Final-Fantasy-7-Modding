# Task: build playtest .bin (CSR + single-disc + movies)

This is the full stack for LOSLAKE1 (#637) manip FMV and general single-disc CSR playtest.
**Movies pack is required.** Core-only plays pristine D1 jairofal (rocket family) at #637.

Needs:

- This repo (Final-Fantasy-7-Modding) on latest main
- Sibling repo Final-Fantasy-7-CSR (csr-v0.14.1 base layer)
- Pristine NTSC-U Disc 1: workspace/pristine/FINALFANTASY7_D1.bin
- Pristine Disc 2 (for prove script only): workspace/pristine/FINALFANTASY7_D2.bin

## 1. Pull

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only
git -C ../Final-Fantasy-7-CSR pull --ff-only
```

## 2. Build the playtest image (three layers)

```bash
cd /path/to/Final-Fantasy-7-Modding

PRISTINE=workspace/pristine/FINALFANTASY7_D1.bin
CSR_LAYER=../Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json
CORE_LAYER=builder/single-disc-on-csr-v0.1.1/layers/disc1.layer.json
MOVIE_LAYER=builder/single-disc-csr-manip-movies-v0.1.0/layers/disc1.layer.json
OUT=workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.bin

# Layer 1: pristine D1 -> CSR base
python3 scripts/apply_layer.py \
  "$PRISTINE" \
  "$CSR_LAYER" \
  -o workspace/iso-extract/ff7_d1_csr_base_local.bin

# Layer 2: + single-disc core (fields/SNOVA/asks — NOT movies)
python3 scripts/apply_layer.py \
  workspace/iso-extract/ff7_d1_csr_base_local.bin \
  "$CORE_LAYER" \
  -o workspace/iso-extract/ff7_d1_csr_sd_core_local.bin

# Layer 3: + manip movies (CANONON into JAIROFAL for #637)
# SKIP THIS => same wrong D1 jairofal clip as pristine disc 1
python3 scripts/apply_layer.py \
  workspace/iso-extract/ff7_d1_csr_sd_core_local.bin \
  "$MOVIE_LAYER" \
  -o "$OUT"

ls -lh "$OUT"
```

## 3. Make a .cue (DuckStation)

```bash
cd workspace/iso-extract
BIN=ff7_d1_playtest_csr_sd_movies.bin
printf 'FILE "%s" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' "$BIN" \
  > ff7_d1_playtest_csr_sd_movies.cue
```

Open the .cue (or .bin) in DuckStation. Playtest file is:

    workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.bin

## 4. Prove movies pack applied (before playtest)

```bash
cd /path/to/Final-Fantasy-7-Modding
python3 << 'PY'
from pathlib import Path
import sys, hashlib
sys.path.insert(0, "scripts")
from psx_mode2_iso import extract_file, find_file

out = Path("workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.bin").read_bytes()
d2 = Path("workspace/pristine/FINALFANTASY7_D2.bin").read_bytes()
d1 = Path("workspace/pristine/FINALFANTASY7_D1.bin").read_bytes()
j = extract_file(out, "MOVIE/JAIROFAL.MOV")
c = extract_file(d2, "MOVIE/CANONON.MOV")
v = extract_file(d1, "MOVIE/JAIROFAL.MOV")
m = find_file(out, "MOVIE/JAIROFAL.MOV")
print("OUT bytes", len(out))
print("JAIROFAL ISO", m)
print("size", len(j), "CANONON", len(c), "vanilla_d1", len(v))
print("playtest==CANONON", j == c)
print("playtest==vanilla_jairofal", j == v)
print("sha playtest", hashlib.sha256(j).hexdigest()[:16])
print("sha CANONON ", hashlib.sha256(c).hexdigest()[:16])
if j != c:
    raise SystemExit("FAIL: movies pack missing or wrong — do not playtest yet")
print("OK — playtest bin has CANONON in JAIROFAL slot")
PY
```

Expect: playtest==CANONON True, size 15071232.

## 5. What each intermediate bin is

| File | Stack | Movies |
|------|-------|--------|
| ff7_d1_csr_base_local.bin | CSR only | vanilla |
| ff7_d1_csr_sd_core_local.bin | CSR + single-disc core | vanilla D1 (jairofal at #637) |
| **ff7_d1_playtest_csr_sd_movies.bin** | CSR + core + **manip-movies** | **CANONON at #637 — use this** |

## 6. LOSLAKE1 (#637) short reminder

- Pristine D2 plays CANONON; pristine D1 plays jairofal. Retail is intentional.
- Single-disc uses disc-1 rules. Movies pack copies CANONON into JAIROFAL.MOV + MOVIE_ID.
- Site builder can cache old layers. Local apply_layer only uses your git clone.

## 7. Optional: site builder instead of local

1. Hard-refresh https://individualcontributor.dev/builder/
2. Base: CSR; Single-disc: on; **no** CSR+ scene packs
3. Build zip from pristine D1
4. APPLIED.txt must list both single-disc-on-csr and single-disc-csr-manip-movies

## 8. Verify config (optional)

```bash
python3 scripts/verify_builder_config.py \
  --pristine workspace/pristine/FINALFANTASY7_D1.bin \
  --disc 1 \
  --base csr-v0.14.1 \
  --addon single-disc-on-csr-v0.1.1 \
  --addon single-disc-csr-manip-movies-v0.1.0
```

---

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
