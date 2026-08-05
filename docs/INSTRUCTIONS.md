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


# DuckStation debugger — LOSLAKE1 wrong FMV (#637)

Use when playtest still shows rocket/launch-pad clip. Capture movie path (id + LBA).

**Always put new debugger findings back into this file** when the procedure changes.

## 0. Only debug the movies playtest bin

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only
python3 mods/single-disc/scripts/build_playtest_bin.py
ls -lh workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.bin
```

Must be **766084032 bytes** (~731 MB). If ~714 MB, movies missing — stop.

Open **only**:

    workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.cue

Host LBA check:

```bash
python3 -c "
from pathlib import Path; import sys; sys.path.insert(0, "scripts")
from psx_mode2_iso import find_file
b = Path("workspace/iso-extract/ff7_d1_playtest_csr_sd_movies.bin").read_bytes()
print("JAIROFAL", find_file(b, "MOVIE/JAIROFAL.MOV"))
print("RCKTFAIL", find_file(b, "MOVIE/RCKTFAIL.MOV"))
'
```

Current packs (verified):

| File | LBA | Size | Content on playtest |
|------|----:|-----:|---------------------|
| JAIROFAL.MOV (eng id 47) | **318357** | **15071232** | **CANONON** (not vanilla jairofal) |
| RCKTFAIL.MOV (eng id 45) | **245435** | 13154304 | vanilla rcktfail (unchanged) |
| vanilla jairofal (reference) | 258385 | 4700160 | only if movies pack missing |

Image on disk is correct for id 47 if size is 766084032 and JAIROFAL==CANONON.

## 1. Setup

1. Enable debugger.
2. Boot playtest .cue.
3. Set execute breakpoint:

```text
0x800CCE94
```

MOVIE (0xF9) handler entry. FIELD base 0x800A0000.

4. Reach LOSLAKE1. When the **wrong FMV starts**, the breakpoint should hit
   (Hit count >= 1). Leave it **paused**.

## 2. You are paused at the right place when

| UI | Good | Bad |
|----|------|-----|
| PC / highlight | **0x800CCE94** (lui / first MOVIE ops) | random addr |
| Breakpoint list | 0x800CCE94 Execute, Hit count **>= 1** | Hit count 0 |
| Memory pane | address **8009D820** or **800722C0** | **00000000** (useless) |

First instructions at entry (for sanity):

```text
0x800CCE94  lui  v0, 0x800A
0x800CCE98  lbu  v0, -0x27E0(v0)   # loads *0x8009D820
0x800CCE9C  addiu sp, sp, -24
0x800CCEA0  andi  v0, v0, 3
```

So **u8[0x8009D820] & 3** is a **movie state**, not the disc movie id.
Movie **id (45 vs 47)** is usually set earlier by PMVIE; dump RAM below + CD LBA.

## 3. While still paused — dump these (required)

### 3a. Memory goto (do not leave memory at 0x0)

```text
8009D820     # first byte handler reads (state); dump 16+ bytes
800722C0     # 32 bytes (includes 0x800722C4)
800716CC     # 16 bytes (loaded early in this handler)
80071C10     # 32 bytes
```

Record:

- u8 **0x8009D820**
- u8 **0x800722C4**
- hex **800722C0-800722DF**
- hex around **800716CC**

### 3b. Registers

Screenshot register panel is fine. At bare entry, v0 often still looks like
0x800CCE94 (lui of handler). a0 may be entity-related later — id is in RAM/CD.

### 3c. Best signal — ISO LBA of the stream

If DS logs CD/ISO sector reads, note LBA when FMV data streams:

| LBA | Meaning |
|----:|---------|
| **318357** | CANONON (id 47 pack) — inject OK |
| **258385** | vanilla JAIROFAL — wrong bin / MOVIE_ID not used |
| **245435** | RCKTFAIL (id 45) — different movie than 47 |
| other | send the number |

### 3d. Optional step further

Step Over a few times deeper into the handler, dump 8009D820 + 800722C0 again.

## 4. Makou on the same playtest .bin

1. Field loslake1 / #637
2. Play movie that matches on-screen clip
3. Note **Set next movie** full line + **id**

Makou order = engine id (not ISO A-Z). Disc 1:

| Id | Name |
|---:|------|
| 45 | rcktfail (rocket fail / pad family) |
| 46 | jairofly |
| 47 | jairofal (triplet with D2 canonon) |
| 48 | gold7 |
| 54+ | No54, No55, ... |

Id 47 D1=jairofal / D2=canonon. Single-disc uses D1 slot; pack puts CANONON bytes there.

## 5. What to send back

1. Path of .bin/.cue DS opened
2. Bin size (must be 766084032 for current packs)
3. u8 0x8009D820, u8 0x800722C4
4. Hex dumps 800722C0-800722DF, 8009D820-8009D82F
5. Movie LBA if available (318357 / 258385 / 245435 / other)
6. Makou Set next movie line + id
7. Screenshot OK if memory address bar shows 8009D820 or 800722C0 (not 00000000)

## 6. Interpretation

| Result | Meaning |
|--------|---------|
| LBA 318357 | Pack stream (CANONON) is what CD read |
| LBA 258385 | Vanilla jairofal still read |
| LBA 245435 | rcktfail id 45 — not fixed by CANONON->JAIROFAL |
| Size ~714MB | Core-only; rebuild playtest bin |
| BP hit, mem at 0x0 only | Right BP, wrong memory pane — fix goto |

## 7. Playtest image sanity (agent/host)

After git pull, agent or operator can re-check:

```bash
python3 mods/single-disc/scripts/build_playtest_bin.py
# must print playtest==CANONON True
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
