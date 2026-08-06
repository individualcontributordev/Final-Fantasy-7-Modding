# Ending / credits movies (D3) vs single-disc D1 space

**Date:** 2026-08-07  
**Status:** measured on pristine D3 + playtest bin `ff7_d1_playtest_csr_sd_movies.bin` (766340400 bytes)

## Symptom

After the final battle on single-disc D1: wrong/random short video (wrong `MOVIE_ID` slot), then black screen and silence. True credits streams live on **Disc 3 only**.

## Disc 3 ending-related MOVIE files (not on pristine D1)

| File | Size (MiB) | Notes |
|------|----------:|-------|
| ENDING2E.MOV | **156.45** | Main long ending/credits stream |
| ENDING3E.MOV | 26.83 | Trailer piece after / with ending |
| ENDING01.MOV | 17.62 | Shorter ending segment |
| LAST4_4.MOV | 10.44 | Late game (not full credits) |
| LASTFLOR.MOV | 2.98 | Endgame (seed deferred; slot clash) |
| LAST4_3 / LASTMAP / LAST4_2 .BIN | &lt;1 | Small; partly already in movie seed |

**All three ENDING\*.MOV together ≈ 200.9 MiB** (payload). Image growth ≈ payload rounded up to 2048-byte sectors × 2352 ≈ **~231 MiB** if appended.

Field scan (older inventory) ties ENDING2E to endgame maps (e.g. BLIN64 / JUNIN7 / ZMIND3 paths); ENDING01/ENDING3E also appear on D3-only plays.

## Free space on current single-disc playtest

| Image | Size | Sectors | Free vs ~80 min (360000 sec) |
|-------|-----:|--------:|-----------------------------:|
| Playtest (CSR + main 0.1.2 + movies 0.1.2) | 766340400 | 325825 | **~34175 sec ≈ 76.7 MiB** |

| Target | Need (≈ ISO data sectors) | ≈ image MiB | Fits in 76.7 MiB free? |
|--------|--------------------------:|------------:|:----------------------:|
| ENDING01.MOV alone | 9023 | 20.2 | **yes** |
| ENDING3E.MOV alone | 13736 | 30.8 | **yes** |
| ENDING01 + ENDING3E | 22759 | 51.0 | **yes** |
| **ENDING2E.MOV alone** | **80104** | **179.7** | **no** |
| All three ENDING\* | 102863 | 230.7 | **no** |

Also over a ~74 min budget (almost no free on this playtest).

## Conclusion

- **Cannot** put the full Disc 3 credits package on the current single-disc D1 image without going past a normal 80‑minute CD (ENDING2E alone is larger than remaining free space).
- Repo whitelist already said: never include ENDING2E (~156 MB) — confirmed by numbers.
- Smaller ending pieces (01 and/or 03) **could** fit in free space, but they are **not** a substitute for the long ENDING2E credits the post-final path expects.
- Full credits on one CD needs either: reclaim **≥ ~180 MiB** of other D1 movie (or other) data, use larger media / multi-session strategy, or **skip/stub** the missing Play and jump to staff/title without the FMV.

## Possible directions (not implemented)

1. **Stub / trim field Play** on the final credits map(s) so black silence becomes an intentional cut (staff BIN / return to title) — gameplay-complete single-disc without the video.
2. **Reclaim large D1 movies** unused on the CSR single-disc route (e.g. OPENINGE 37 MiB, BOOGSTAR 24 MiB, …) until ENDING2E fits — high risk, needs play route audit.
3. **Ship ENDING01+03 only** — may still look wrong if the engine plays id for ENDING2E.
4. **Hybrid:** external second track / larger burn target (not standard CD-R single-disc goal).

## Related

- `mods/single-disc/patches/csr-manip-movie-whitelist.md` — ENDING2E never include
- `mods/single-disc/patches/field-movie-d2d3-missing-on-d1.md` — D3 ending field hits
- Movies pack: cumulative `single-disc-csr-manip-movies-v0.1.2` (no ending files today)
