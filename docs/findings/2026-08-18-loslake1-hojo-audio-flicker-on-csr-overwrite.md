# Finding: LOSLAKE1/Hojo audio flicker — single-disc-on-csr reverted Form2 fix

**Date:** 2026-08-18
**Status:** fixed (edited `builder/single-disc-on-csr/layers/disc1.layer.json` directly)
**Report:** Movie plays fine, but the sound flickers on the ending movie and/or LOSLAKE1 (Bugenhagen waterfall).

## Cause

`single-disc-csr-manip-movies-v0.1.4` correctly writes MOVIE_ID rows 47
(JAIROFAL/LOSLAKE1) and 52 (CAR_1209/Hojo CANONHT2) with Form2 engine length
(`nsec*2336`) and the source disc's aux values (see
`2026-08-12-manip-movies-dual-audio-movie-id.md`).

`single-disc-on-csr` applies **after** manip-movies in `APPLY_ORDER`. Its
layer JSON contained 3 stray byte-writes (at MOVIE_ID row 47 `size` field and
row 52 `size`/`a` fields) left over from when that layer was diffed against a
pre-manip-movies baseline. Those writes silently reverted the size field back
toward a plain ISO byte count, corrupting the Form2 metadata manip-movies had
just set:

| Row | Field | Manip-movies (correct) | on-csr overwrite (bug) |
|-----|-------|------------------------|------------------------|
| 47 | size | 17190624 (Form2) | 31848448 |
| 52 | size | 5977824 (Form2) | 6027488 |

Wrong `eng_size` makes the XA audio decoder misread sector boundaries for
these two Form2 movies while the STR video track still decodes fine — audio
flickers/crackles, video looks normal. Matches the report exactly.

## Fix

Removed the 3 stray records (file offsets `298608536`, `298608637`,
`298608639`) from `builder/single-disc-on-csr/layers/disc1.layer.json` so it
no longer touches those bytes; manip-movies' Form2 values pass through
untouched.

Verified: rebuilt full stack (manip-movies + on-csr + parts 2-10 + endings
parts 1-7) locally; rows 47/52 now match Form2 values; only remaining
DATA-area difference vs the working reference bin is an unrelated pre-existing
row 46 (MAINPLR.MOV) mismatch, tracked separately.

## Not fixed here

The ENDING2E.MOV LBA-collision corruption (documented separately — ending
movie clobbers ~13 other movies' sectors) is a distinct, unrelated bug from
this audio-only flicker. Not touched by this change.
