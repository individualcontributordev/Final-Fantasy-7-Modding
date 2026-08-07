# Task: retest LOSLAKE1 + endings (CD image v7)

## Why LOSLAKE1 broke

Your DS log (recovered from git; saved as
`docs/findings/2026-08-07-loslake1-ending-cd-log.txt`):

```text
setloc (55, 41, 25)   → ISO LBA 250450
Read sector 250600 … submode 0x48
```

LOSLAKE1 **must** read Form2 **CANONON** at LBA **250450** (CSR / manip-movies).  
Placing continuous **ENDING2E** at Disc 3 LBAs overwrote that range with
ending stream (`0x48`), so the lake FMV stopped playing.

## What v7 does

Same CD-sized build as before, then **punch CANONON** raw sectors back at
250450 after endings:

1. CSR + core + movies 0.1.2  
2. LASTMAP v5 + LAS4_0  
3. D3 endings at D3 LBAs (163608 ENDING01, etc.)  
4. **CANONON Form2 @ 250450** (LOSLAKE1)

Still **766340400** bytes — 80-min CD OK.

**Tradeoff:** mid-ENDING2E (LBA 250450–257808, ~7359 sec) is CANONON, not
credits. Ending **start** and other ending streams stay correct.

## What you do

```bash
cd /path/to/Final-Fantasy-7-Modding
git pull --ff-only
python3 mods/single-disc/scripts/build_ending_credits_test_bin.py
# open:
# workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

Test:

1. **LOSLAKE1** lake FMV (should play again)  
2. Post-final **endings** (may glitch mid long credits)  

## Reply

1. LOSLAKE1 OK?  
2. Endings OK / mid-credit glitch?  
3. Bin size  
