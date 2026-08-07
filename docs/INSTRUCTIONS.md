# Status: v7 log analyzed (ending skip)

## What your DuckStation log shows

Saved: `docs/findings/2026-08-07-ending-v7-skip-log.txt`

| | |
|--|--|
| Capture window | ~3 s wall, DS **250167–250620** only |
| ISO LBAs | **250017–250470** |
| File | Mid **ENDING2E** (starts 197242) |
| Offset into ENDING2E | ~**52775** of 80104 (~**66%**) |
| Transition | ISO **250450**: submode **0x48/0x64 → 0x42** |
| Meaning | Credits stream hits the **CANONON hole**, then Pause |

There are **no** reads of LASTFLOR / ENDING01 / ENDING3E starts (**162081 / 163608 / 172631**) in this paste. Either those already finished before logging, or the log was started mid-roll.

That matches: **short first bit → jump into scrolling credits → rest including stars**, with a glitch when the roll crosses **250450**.

## Cause (expected on v7)

CANONON is punched at **250450–257808** for LOSLAKE1.  
ENDING2E must occupy that range on Disc 3 layout → **cannot be continuous** while lake works.

## What to do next (pick one)

**A. Confirm LOSLAKE1** still plays full on this same v7 cue (main v7 goal).

**B. Prioritize clean long credits** — burn/test build **without** the CANONON punch  
(endings continuous; lake will break again until hard-seek is RE’d).

**C. Full ending CDROM log** from **before** the first ending FMV through stars  
(enable logging earlier; we need setlocs at 162081 / 163608 / 172631 / 197242).

## Current test image

```text
workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

Rebuild: `python3 mods/single-disc/scripts/build_ending_credits_test_bin.py`

## Reply

1. LOSLAKE1 OK on v7?  
2. Prefer clean credits (B) or lake (current A)?  
3. Optional: fuller ending log (C)  
