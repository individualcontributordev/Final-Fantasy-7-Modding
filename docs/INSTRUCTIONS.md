# Task: test v7 (LOSLAKE1 + endings, CD-sized)

## What v7 is

Same CD image (~731 MiB) as working endings, plus **CANONON** restored at
LBA **250450** so LOSLAKE1 can play again.

| Check | Expect |
|-------|--------|
| LOSLAKE1 lake FMV | Full CANONON (should work) |
| Endings after final battle | Play; possible glitch mid long credits |
| Bin size | **766340400** |

Mid-ENDING2E (LBA 250450–257808) is CANONON on purpose so the lake works.

## What you do

### 0. Update

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only
```

### 1. Rebuild (if bin missing or unsure)

```bash
python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
```

Expect last lines: CANONON OK @ 250450, size 766340400, free80=34175.

### 2. Open

```text
workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

Do **not** use `ff7_d1_playtest_csr_sd_movies.cue` for this test.

### 3. Smoke

1. **LOSLAKE1** — lake / Bugenhagen FMV plays with video+audio  
2. **After final battle** — ending sequence / credits play (note any mid-roll hitch)  
3. Optional: bin size still 766340400  

### 4. Reply

1. LOSLAKE1: OK / fail (what you saw)  
2. Endings: OK / glitch / fail  
3. Bin size if you checked  
