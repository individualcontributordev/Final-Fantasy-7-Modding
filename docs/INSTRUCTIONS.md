# Task: put CSR Disc 1 DEL1 on the single-disc image

## Why

Single-disc ships as **one Disc 1 image**. CSR’s trim on **DEL1** (field #441)
is on **CSR Disc 1**: it removes the map jump to DEL2 (field #442). That is the
file that belongs on the single-disc image so Costa keeps the CSR cut.

## What you do this pass

1. Pull
2. Confirm the published single-disc core already has that CSR Disc 1 DEL1
3. Rebuild playtest and spot-check Costa / DEL1

If step 2 fails, section 4 copies CSR Disc 1’s `FIELD/DEL1.DAT` onto a work image
and rebuilds the core layer.

Repos layout:

```text
Final-Fantasy-7-Modding/
Final-Fantasy-7-CSR/          (sibling)
```

---

## 0. Update

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only
git -C ../Final-Fantasy-7-CSR pull --ff-only
```

Need: `workspace/pristine/FINALFANTASY7_D1.bin` (and D2 only if you re-run optional compares).

---

## 1. (Optional) See CSR Disc 1 vs CSR Disc 2 scripts for DEL1

```bash
cd /path/to/Final-Fantasy-7-Modding

python3 scripts/compare_field_dat.py csr:1 csr:2 --field DEL1 \
  -o workspace/iso-extract/del1-csr-d1-vs-d2.md
```

Report shows the script gaps (including `border1` / jump to 442). You can skip
this if you only want the pack check.

---

## 2. Confirm published core layer has CSR Disc 1 DEL1

```bash
cd /path/to/Final-Fantasy-7-Modding

python3 << 'PY'
from pathlib import Path
import json, sys
sys.path.insert(0, "scripts")
from apply_layer import apply_layer
from psx_mode2_iso import extract_file
from field_compare import compare_bytes

root = Path(".")
pristine = (root / "workspace/pristine/FINALFANTASY7_D1.bin").read_bytes()
csr_layer = Path("../Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json")
core_layer = root / "builder/single-disc-on-csr-v0.1.1/layers/disc1.layer.json"

img = bytearray(pristine)
apply_layer(img, json.loads(csr_layer.read_text()))
csr_del1 = extract_file(bytes(img), "FIELD/DEL1.DAT")

apply_layer(img, json.loads(core_layer.read_text()))
core_del1 = extract_file(bytes(img), "FIELD/DEL1.DAT")

diff = compare_bytes(csr_del1, core_del1, a_label="CSR_D1_DEL1", b_label="core_layer_DEL1")
print("classification:", diff.classification)
print("script slots differ:", len(diff.script_diffs))
print("same bytes:", csr_del1 == core_del1)
if csr_del1 != core_del1:
    raise SystemExit("FAIL: core DEL1 is not CSR Disc 1 — do section 4")
print("OK — single-disc core DEL1 == CSR Disc 1 DEL1")
PY
```

**Pass:** `OK — single-disc core DEL1 == CSR Disc 1 DEL1`
**Fail:** section 4.

---

## 3. Rebuild playtest

```bash
cd /path/to/Final-Fantasy-7-Modding
python3 mods/single-disc/scripts/build_playtest_bin.py
```

Open **only**:

```text
workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.cue
```

(size about **766340400** bytes).

In-game check: Costa boat / DEL1 keeps the CSR cut (no jump into DEL2 #442).

Optional playtest file check:

```bash
python3 << 'PY'
from pathlib import Path
import json, sys
sys.path.insert(0, "scripts")
from apply_layer import apply_layer
from psx_mode2_iso import extract_file
from field_compare import compare_bytes

root = Path(".")
img = bytearray((root / "workspace/pristine/FINALFANTASY7_D1.bin").read_bytes())
apply_layer(
    img,
    json.loads(Path("../Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json").read_text()),
)
ref = extract_file(bytes(img), "FIELD/DEL1.DAT")
play = extract_file(
    (root / "workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.bin").read_bytes(),
    "FIELD/DEL1.DAT",
)
d = compare_bytes(ref, play, a_label="CSR_D1", b_label="playtest")
print("playtest DEL1 vs CSR D1:", d.classification, "same", ref == play)
if ref != play:
    raise SystemExit("FAIL playtest DEL1")
print("OK")
PY
```

---

## 4. Only if step 2/3 failed — force CSR Disc 1 DEL1 in

### 4a. Export CSR Disc 1 DEL1

```bash
cd /path/to/Final-Fantasy-7-Modding
mkdir -p workspace/iso-extract/field-merge

python3 << 'PY'
from pathlib import Path
import json, sys
sys.path.insert(0, "scripts")
from apply_layer import apply_layer
from psx_mode2_iso import extract_file

root = Path(".")
out = root / "workspace/iso-extract/field-merge/DEL1_csr_d1.DAT"
img = bytearray((root / "workspace/pristine/FINALFANTASY7_D1.bin").read_bytes())
apply_layer(
    img,
    json.loads(Path("../Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json").read_text()),
)
data = extract_file(bytes(img), "FIELD/DEL1.DAT")
out.write_bytes(data)
print("wrote", out, len(data), "bytes")
PY
```

### 4b. CSR work image + inject

```bash
cd /path/to/Final-Fantasy-7-Modding

python3 scripts/apply_layer.py \
  workspace/pristine/FINALFANTASY7_D1.bin \
  ../Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json \
  -o workspace/iso-extract/ff7_d1_csr_work.bin

python3 << 'PY'
from pathlib import Path
import sys
sys.path.insert(0, "scripts")
from psx_mode2_iso import replace_file_padded, extract_file

work = Path("workspace/iso-extract/ff7_d1_csr_work.bin")
dat = Path("workspace/iso-extract/field-merge/DEL1_csr_d1.DAT").read_bytes()
img = bytearray(work.read_bytes())
replace_file_padded(img, "FIELD/DEL1.DAT", dat)
work.write_bytes(img)
assert extract_file(bytes(img), "FIELD/DEL1.DAT") == dat
print("injected FIELD/DEL1.DAT OK", len(dat))
PY
```

### 4c. Diff work bin into core layer (on top of CSR base)

```bash
cd /path/to/Final-Fantasy-7-Modding

python3 scripts/apply_layer.py \
  workspace/pristine/FINALFANTASY7_D1.bin \
  ../Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json \
  -o workspace/iso-extract/ff7_d1_csr_base_for_diff.bin

# Work bin must include ALL single-disc core edits (not only DEL1) before a
# full re-diff. If unsure, paste FAIL output in chat instead of re-diffing alone.

python3 scripts/bin_diff_to_layer.py \
  workspace/iso-extract/ff7_d1_csr_base_for_diff.bin \
  workspace/iso-extract/ff7_d1_csr_work.bin \
  -o builder/single-disc-on-csr-v0.1.1/layers/disc1.layer.json \
  --id single-disc-on-csr-v0.1.1-disc1 \
  --description "single-disc on CSR D1 (FIELD/DEL1.DAT = CSR Disc 1)"
```

Then re-run **section 2** and **section 3**.

---

## 5. When DEL1 is done — reply

Paste:

1. Section 2 result (`OK` or `FAIL` + text)
2. Optional playtest DEL1 check
3. Short play note (Costa / DEL1 → 442 jump fixed or not)

After DEL1 is confirmed, the next maps get their own instruction pass
(`BLACKBGB` from CSR Disc 1, `LOST2` from CSR Disc 2, then the other shared maps).

---

## Archive (older notes)

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








































































































































































