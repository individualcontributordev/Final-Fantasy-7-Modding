# Ending credits test inject

**Date:** 2026-08-07  
**Status:** v6 — D3 absolute LBA placement

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
| v6 | (test) | raw D3 sectors + MOVIE_ID at D3 LBAs |

## v6 layout

Tool: `mods/single-disc/scripts/alias_d3_ending_lbas_on_d1.py`

| id | file | LBA |
|---:|------|----:|
| 23 | LASTMAP.BIN | 161972 |
| 24 | LASTFLOR.MOV | 162081 |
| 25 | ENDING01.MOV | 163608 |
| 26 | ENDING3E.MOV | 172631 |
| 29 | ENDING2E.MOV | 197242 |

Overwrites whatever D1 movies previously occupied those LBA ranges.  
Builder: `build_ending_credits_test_bin.py` + `ending-lastmap-v5.DAT`.

## Play

```text
workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

DuckStation only; not CD/builder pack.
