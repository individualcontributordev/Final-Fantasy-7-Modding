# INSTRUCTIONS — rebuild Disc 1 on single-disc v0.1.24 (PARASHOT playtest)

## Why

v0.1.24 + builder apply order fix path FMVs (PARASHOT / NRCRL) that movies
used to clobber. Offline regression suite is green. You need a **new** builder
Disc 1 image — older builds (0.1.23 and earlier) will still miss PARASHOT.

## Build (browser)

1. Open https://individualcontributor.dev/builder/
2. Hard-refresh (Cmd+Shift+R) so pack list + apply order update
3. Base: **CSR**
4. Mods: **Single-disc** only (version badge **v0.1.24**). CSR+ off for this test
5. Confirm APPLIED (or pack list) includes:
   - single-disc-csr-manip-movies-v0.1.4 (auto)
   - single-disc-on-csr-v0.1.24
   - endings parts if they auto-include (OK to leave on)
6. Build **Disc 1** only; download zip; load the .bin/.cue in DuckStation

## Playtest (in order if you can)

| Spot | Expect |
|------|--------|
| Highwind deck FSHIP_12 | Full **PARASHOT** FMV, Cloud placed correctly |
| MD8_5 (#731) after that path | Clean NRCRLB FMV; field not glitched |
| MD8_52 | NRCRL then Highwind |
| Optional smoke | Hojo (CANON_2 audio OK), disc break LOSIN2 to LOST2, waterfall LOSLAKE |

## Evidence

Paste into a reply (or commit under workspace/ if you prefer):

- APPLIED.txt contents from the zip
- Pass/fail for PARASHOT + MD8_5
- Any freeze/glitch notes (no Cheat Engine attached)

## Agent note

Repo tests already cover stack invariants. From Final-Fantasy-7-Modding:

    python3 -m pytest tests/ -q
