# Task: ending credits test v5

## Why v4 still froze

DuckStation log showed Form2 reads in **ONTRAIN** (MOVIE_ID **id 23**), then:

- `Invalid MDEC command …`
- page fault at `0x00000000`

On Disc 3, **id 23 = LASTMAP.BIN** (Form1 **camera**, not FMV).  
LASTMAP does `PMVIE 23` then later `AD` `MOVIE` while that id is still selected.  
Feeding a Form2 train FMV (or any MDEC stream) at id 23 crashes the same way as v3.

## What v5 does

1. **MOVIE_ID 23** ← real D3 **LASTMAP.BIN** Form1 + D3 aux (camera).  
2. **LASTMAP field patch**: remove early **`MOVIE`** on AD S31  
   (`MVCAM` only). **PMVIE 23/24** kept. Final **AD3 `MOVIE`** still runs  
   after **PMVIE 24** → LASTFLOR.  
3. Form2 D3 streams on **24 / 25 / 26 / 29** (LASTFLOR, ENDING*).  
4. Pristine **LAS4_0** (PMVIE 25 + MOVIE).

Bin ~**1008274176** — DuckStation only.

## What you do

1. Pull  
2. Open ending-test cue (rebuild if needed)  
3. LASTMAP → end credits  
4. Reply: freeze? what played? sound?  

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

Expect ~**1008274176** bytes.

---

## 2. Rebuild if needed

```bash
python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
```

---

## 3. Smoke

- No MDEC crash on LASTMAP  
- LASTFLOR / ENDING* should play for the real FMV path  
- Camera path may load id 23 without full-motion train footage  

---

## 4. Reply

1. Bin size  
2. What played  
3. Freeze yes/no · sound yes/no  
