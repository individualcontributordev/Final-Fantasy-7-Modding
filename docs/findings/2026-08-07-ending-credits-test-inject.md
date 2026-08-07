# Ending credits test inject

**Date:** 2026-08-07
**Status:** v7 — CD-sized + CANONON@250450 restored for LOSLAKE1

## Evidence (v5 post-battle black screen)

DuckStation:

```text
CDROM setloc (36, 23, 33)
Seek … failed
```

MSF 36:23:33 → ISO LBA **163608** = pristine Disc 3 **ENDING01.MOV** start.  
MOVIE_ID on the test image pointed id 25 at grown **325825** with correct
payload/meta — engine still sought **163608**.  

So this path behaves like LOSLAKE1/CANONON: **hard absolute LBA**, not “any
LBA stored only in a rewritten table and respected everywhere.”

## Failure ladder

| Ver | Result | Cause |
|-----|--------|--------|
| v0–v2 | no credits / freeze | field ops / 2048 size field |
| v3–v4 | MDEC crash | id23 wrong stream type / early MOVIE |
| v5 | LASTMAP OK; black after battle | ENDING01 sought at D3 LBA, empty |
| v6 | **works** (user DS) | raw D3 sectors + MOVIE_ID at D3 LBAs |

## v6 layout

Tool: `mods/single-disc/scripts/alias_d3_ending_lbas_on_d1.py`

| id | file | LBA |
|---:|------|----:|
| 23 | LASTMAP.BIN | 161972 |
| 24 | LASTFLOR.MOV | 162081 |
| 25 | ENDING01.MOV | 163608 |
| 26 | ENDING3E.MOV | 172631 |
| 29 | ENDING2E.MOV | 197242 |

Overwrites D1 movies under those LBA ranges (~17 full + partials).
**CD size:** image stays **766340400** B (325825 sec) — **fits 80‑min**
(~360000 sec) with ~76 MiB free. No EOF grow.

## v7: LOSLAKE1 + endings (CD)

Log `docs/findings/2026-08-07-loslake1-ending-cd-log.txt`: after v6 CD
build, LOSLAKE1 sought **55:41:25** (LBA **250450**) and read ENDING2E
(`submode 0x48`) instead of CANONON Form2 (`0x42`).

**Fix:** after D3 ending alias, punch full D2 CANONON raw sectors at
250450 again (builder step 4). No image grow.

| Range | Content |
|-------|---------|
| 163608+ | ENDING01 (intact) |
| 197242..250449 | start of ENDING2E (intact) |
| **250450..257808** | **CANONON** (LOSLAKE1; holes mid-credits) |
| 257809..277345 | rest of ENDING2E (restored after punch window) |

Builder: `build_ending_credits_test_bin.py`. Not a CDN layer (~200 MiB delta).

## v7 playtest log (ending skip)

`docs/findings/2026-08-07-ending-v7-skip-log.txt` (from user paste):

- Only ~3 s of CD activity: ISO **250017–250470** mid-ENDING2E.
- At ISO **250450**, submode switches **0x48 → 0x42** (ENDING2E → CANONON punch).
- Then CDROM Pause. No LASTFLOR/ENDING01/ENDING3E seeks in this clip.
- Matches report: jump into scrolling credits / glitch when roll hits the hole.

## Play / burn

```text
workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

MODE2/2352. Local build from pristine D1–D3.
