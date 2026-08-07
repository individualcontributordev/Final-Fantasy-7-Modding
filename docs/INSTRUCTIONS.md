# Task: ending credits test v6 (D3 absolute LBAs)

## What worked / what failed last time

- **v5 fixed LASTMAP freeze** (id23 = camera BIN; early MOVIE removed).
- After final battle: text boxes, then **black + no sound** (not a hard freeze).

Log:

```text
setloc (36, 23, 33)   → ISO LBA 163608
ReadS … Seek … failed
```

**163608 is Disc 3’s ENDING01 start.**  
Our inject had put ENDING01 at grown LBA **325825** and updated MOVIE_ID —  
the game still sought the **Disc 3 absolute address**. Seek failed → black silence.

Same idea as CANONON @ LBA **250450**.

## What v6 does

1. LASTMAP v5 field patch + pristine LAS4_0.  
2. Copy D3 raw sectors for endings to **exact D3 LBAs**:

| id | D3 file | D3 LBA |
|---:|---------|-------:|
| 23 | LASTMAP.BIN | 161972 |
| 24 | LASTFLOR.MOV | 162081 |
| 25 | ENDING01.MOV | **163608** |
| 26 | ENDING3E.MOV | 172631 |
| 29 | ENDING2E.MOV | 197242 |

3. Dirents + MOVIE_ID rows match those LBAs and D3 size/aux.

Bin stays ~**766340400** if endings fit in existing image span (overwrites other D1 movie ranges at those addresses). DuckStation test only.

## What you do

1. Pull  
2. Open ending-test cue (rebuild if needed)  
3. Past final battle → text → should get **ENDING01** (not black)  
4. Reply  

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

---

## 2. Rebuild if needed

```bash
python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
```

---

## 3. Smoke

- LASTMAP still OK (no MDEC crash)  
- After final battle / dialogue: real ending FMV + audio  
- Note black screen or seek errors  

---

## 4. Reply

1. Bin size  
2. What played after text  
3. Freeze / black / sound  
