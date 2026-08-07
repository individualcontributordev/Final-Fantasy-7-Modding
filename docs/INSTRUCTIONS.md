# Task: ending credits test v4 (no LASTMAP.BIN)

## Why v3 froze (MDEC crash)

DuckStation log (pasted earlier into this file) showed:

- `Invalid MDEC command …`
- then page fault at `0x00000000`

Cause: we injected Disc 3 **`LASTMAP.BIN`** into **MOVIE_ID row 23**.

That file is **Form1 data** (submode `0x08`), not a Form2 FMV.  
LASTMAP’s first play path does `PMVIE 23` then `MOVIE` → MDEC fed garbage → freeze.

PMVIE indexes **`MINT/MOVIE_ID.BIN` row numbers**, same on Disc 1 and Disc 3 for the
ending range. The mistake was **bytes**, not “wrong disc’s id table.”

## What v4 does

1. Restore pristine **LASTMAP.DAT** / **LAS4_0.DAT** (ending Play ops).  
2. Inject **only Form2** Disc 3 streams (engine size = D3, usually ×2336):

| MOVIE_ID id | Disc 3 file | Role |
|------------:|-------------|------|
| 24 | LASTFLOR.MOV | LASTMAP final FMV |
| 25 | ENDING01.MOV | LAS4_0 |
| 26 | ENDING3E.MOV | ending |
| 29 | ENDING2E.MOV | long credits |

3. **Do not** put LASTMAP.BIN on id 23. Id 23 stays Disc 1’s **ONTRAIN** FMV  
   (harmless short clip if the first `PMVIE 23` path runs).

Still **~1.0 GB** — DuckStation only.

## What you do

1. Pull  
2. Open ending-test cue (rebuild if missing)  
3. LASTMAP → after final battle / credits  
4. Reply: freeze? what FMV? sound?  

---

## 0. Update

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only
```

---

## 1. Open

```text
workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

Bin size **1008274176**.

Not the normal playtest cue.

---

## 2. Rebuild if needed

```bash
python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
```

---

## 3. Smoke

- Should **not** MDEC-crash / hard freeze on LASTMAP entry movies  
- Expect LASTFLOR + ENDING* (not random Midgar junk forever)  
- Note any short ONTRAIN blip from id 23  

---

## 4. Reply

1. Bin size  
2. What played  
3. Freeze yes/no · sound yes/no  
