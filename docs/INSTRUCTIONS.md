# INSTRUCTIONS — rebuild Disc 1 (Single-disc v0.1.26 boot fix)

## Why 0.1.24 alone worked

0.1.24 never moved MINT/MOVIE_ID.BIN and stays under the CD ~80-minute range.
The path-engine pack broke boot two ways:
1. Moved MOVIE_ID to LBA 363784 (MSF 80:52:34) — DuckStation seek loop
2. Even after in-place MOVIE_ID fix, streams past 80:00 + sticky id@0.1.25 cache

## Fix v0.1.26

New hidden pack id (forces fresh download). Image ends ~79:10. MOVIE_ID stays
at LBA 126959. PARASHOT engine id still wired for MD8_5.

## Build

1. Hard-refresh builder (Cmd+Shift+R) or private window
2. Base: CSR
3. One checkbox: Single-disc badge v0.1.26 (no second row)
4. CSR+ off for this check
5. APPLIED must list:
   - single-disc-csr-manip-movies-v0.1.4
   - single-disc-on-csr-v0.1.24
   - single-disc-on-csr-v0.1.26   (auto; NOT 0.1.25)
6. Build Disc 1 — discard older zips
7. Open the .cue with .bin beside it

## Success

- Boots without Logical seek to [80:52:34] failed spam
- Badge / APPLIED shows 0.1.26 path-engine, not 0.1.25

## Then playtest

| Spot | Expect |
|------|--------|
| FSHIP_12 then MD8_5 (#731) | Full PARASHOT |
| FSHIP_24 (#71), BLIN66_6 (#255) | CSR D2 trims |

## Evidence

- APPLIED.txt (must include v0.1.26, must not need 0.1.25)
- Boot OK / fail
