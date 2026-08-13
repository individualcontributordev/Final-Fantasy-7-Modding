# INSTRUCTIONS — rebuild Disc 1 after MOVIE_ID boot fix

## What broke

DuckStation: Logical seek to [80:52:34] failed (loop).
MSF 80:52:34 = LBA 363784 = where v0.1.25 had moved MINT/MOVIE_ID.BIN
past the ~80-minute CD range. Game could not load the movie table so the
disc looked unloadable.

## Fix (same pack id v0.1.25, rebuilt)

MOVIE_ID grows in place at CSR LBA 126959 (1220 bytes still one sector).
Path-engine FMVs + field PMVIE remaps + FSHIP_24/BLIN66_6 kept.

## Build

1. Hard-refresh https://individualcontributor.dev/builder/
2. Base CSR + Single-disc only (one checkbox, badge v0.1.25)
3. APPLIED order: movies v0.1.4, single-disc-on-csr-v0.1.24, v0.1.25
4. Build Disc 1 (discard any zip from before this fix)
5. Load the .cue in DuckStation (keep .bin and .cue together)

## Success

- Boots past logo/title without infinite CDROM seek failures
- No spam of Seek to [80:52:34] failed

## Then playtest

| Spot | Expect |
|------|--------|
| FSHIP_12 then MD8_5 (#731) | Full PARASHOT |
| FSHIP_24 (#71), BLIN66_6 (#255) | CSR D2 trims |

## Evidence

- APPLIED.txt
- Boot OK / fail + any new DuckStation CDROM lines
