# Ending credits test inject (DuckStation oversize bin)

**Date:** 2026-08-07
**Status:** v3 — fields + Form2 MOVIE_ID size/aux from Disc 3

## Failure ladder

1. **v0 inject-only:** single-disc LASTMAP/LAS4_0 stripped ending MOVIE ops → random clip / black silence.
2. **v2 scripts restored, wrong size field:** inject wrote ISO **2048×sectors** into MOVIE_ID size. Engine needs **2336×sectors** (and D3 aux a/b/c). LASTMAP **froze** on play.
3. **v3:** copy source-disc MOVIE_ID size+aux; keep grown D1 LBA.

## v3 fix (test bin only)

1. Base: playtest (CSR + main 0.1.2 + movies 0.1.2).
2. Restore **pristine** FIELD/LASTMAP.DAT and FIELD/LAS4_0.DAT.
3. Inject D3 streams; MOVIE_ID rows keep **D1 LBA**, rest match **D3**:

| id | D3 source | D1 slot | size field (D3) |
|---:|-----------|---------|----------------:|
| 23 | LASTMAP.BIN | ONTRAIN.MOV | 223000 |
| 24 | LASTFLOR.MOV | MAINPLR.MOV | 3567072 (= nsec×2336) |
| 25 | ENDING01.MOV | SMK.STR | 21077728 |
| 26 | ENDING3E.MOV | SOUTHMK.MOV | 32087296 |
| 29 | ENDING2E.MOV | MONITOR.STR | 187122944 |

Tool: `inject_movies_by_disc_id.py` now reads source MOVIE_ID meta (Form2).
Builder: `build_ending_credits_test_bin.py`

## Play

```text
workspace/iso-extract/ff7_d1_playtest_ending_test.cue
```

Size **1008274176** — DuckStation only.

## Caveats

Overwrites ids 23–26, 29; pristine last-map scripts on this image only.
