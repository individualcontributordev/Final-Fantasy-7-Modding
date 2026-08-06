# Task: confirm BLACKBGB on single-disc (field #103)

## Done last pass

- **DEL1:** section 2 confirm OK — CSR Disc 1 DEL1 is on the single-disc core.

## Why this map is different

`FIELD/BLACKBGB.DAT` is the mid-game hub that **asks which disc** to insert.

| Copy | What it is |
|------|------------|
| CSR Disc 1 / CSR Disc 2 | Still has **four** disc-change ops (`DSKCG`) in `init` |
| Single-disc core | Those four asks **removed** (required for one-disc play) |

CSR D1 vs D2 also differ by **one** `MAPJUMP` order in `init`. The file we keep is
**single-disc’s edited BLACKBGB** (asks gone), not a raw CSR re-copy.

## What you do

1. Pull  
2. Confirm core BLACKBGB has **zero** `DSKCG`  
3. Confirm it is not identical to raw CSR Disc 1 (asks would come back)  
4. Rebuild playtest (optional Costa already OK; hub smoke if you can)

---

## 0. Update

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only
git -C ../Final-Fantasy-7-CSR pull --ff-only
```

---

## 1. Optional — see CSR Disc 1 vs Disc 2

```bash
cd /path/to/Final-Fantasy-7-Modding
python3 scripts/compare_field_dat.py csr:1 csr:2 --field BLACKBGB \
  -o workspace/iso-extract/blackbgb-csr-d1-vs-d2.md
```

Expect: `scripts`, one differing slot (`init`).

---

## 2. Confirm single-disc core BLACKBGB (must pass)

```bash
cd /path/to/Final-Fantasy-7-Modding

python3 << 'PY'
from pathlib import Path
import json, sys
sys.path.insert(0, "scripts")
from apply_layer import apply_layer
from disc_sources import load_csr_image, load_pristine_image
from field_compare import compare_bytes
from field_dat import load_field_dat, decode_ops, fmt_op
from psx_mode2_iso import extract_file

def core_blackbgb() -> bytes:
    img = load_pristine_image(1)
    apply_layer(
        img,
        json.loads(Path("../Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json").read_text()),
    )
    apply_layer(
        img,
        json.loads(Path("builder/single-disc-on-csr-v0.1.1/layers/disc1.layer.json").read_text()),
    )
    return extract_file(bytes(img), "FIELD/BLACKBGB.DAT")

def count_dskcg(dat: bytes) -> list:
    hits = []
    f = load_field_dat(dat)
    for s in f.scripts:
        for raw, name in decode_ops(s.raw):
            if name == "DSKCG":
                hits.append((s.entity, s.slot, fmt_op(raw, name)))
    return hits

core = core_blackbgb()
csr1 = extract_file(bytes(load_csr_image(1)), "FIELD/BLACKBGB.DAT")
hits = count_dskcg(core)
print("core DSKCG count:", len(hits))
for h in hits:
    print(" ", h)
print("core == CSR Disc 1?", core == csr1)
d = compare_bytes(csr1, core, a_label="CSR_D1", b_label="core")
print("CSR D1 vs core:", d.classification, "script_diffs", len(d.script_diffs))
if hits:
    raise SystemExit("FAIL: core still has disc-change asks — blackbg hub broken for single-disc")
if core == csr1:
    raise SystemExit("FAIL: core BLACKBGB is raw CSR (asks would still be present)")
print("OK — single-disc BLACKBGB keeps Ask removal (not raw CSR)")
PY
```

**Pass:** `OK — single-disc BLACKBGB keeps Ask removal (not raw CSR)`  
**Fail:** paste full output (do not re-copy CSR BLACKBGB over core without re-doing Ask removal).

PY
core DSKCG count: 0
core == CSR Disc 1? False
CSR D1 vs core: scripts script_diffs 1
OK — single-disc BLACKBGB keeps Ask removal (not raw CSR)

---

## 3. Rebuild playtest

```bash
cd /path/to/Final-Fantasy-7-Modding
python3 mods/single-disc/scripts/build_playtest_bin.py
```

Open: `workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.cue`

If you reach blackbg hub: **no** “insert disc 2/3” prompt on those four routes.

---

## 4. Reply when done

Paste:

1. Section 2 full output (`OK` or `FAIL`)
2. Playtest build OK if you ran it

---

## Queue after this

| Map | Intent |
|-----|--------|
| LOST2 | Put **CSR Disc 2** file on the single-disc image (break scene) |
| Remaining 7 | Still need a real merge rule each |

Tools: `scripts/README.md`

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








































































































































































