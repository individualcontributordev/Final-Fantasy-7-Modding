# Finding: LOSLAKE1/Hojo audio flicker — retracted, single-disc-on-csr edit was wrong

**Date:** 2026-08-18
**Status:** retracted — the diagnosis and fix below were wrong; reverted same day.
**Report:** Movie plays fine, but the sound flickers on the ending movie and/or LOSLAKE1 (Bugenhagen waterfall).

## What actually happened

The original theory (below, kept for the record) was that 3 records in
`single-disc-on-csr` at file offsets `298608536`, `298608637`, `298608639`
were stray reverts of a Form2 fix `single-disc-csr-manip-movies-v0.1.4`
applies to MOVIE_ID rows 47/52. Those 3 records were removed.

This was validated only by diffing against a reference bin
(`ff7-d1-csr-sd-mov-end.bin`) assumed to be "known-good." **That assumption
was wrong** — the human confirmed the reference bin has the exact same
audio-flicker bug on field 637's movie and the ending movies. Matching it
byte-for-byte does not fix flicker, it just reproduces the same bug.

Worse, removing those 3 records was itself a regression: they are legitimate
CSR corrective overrides on top of `manip-movies`, unrelated to the flicker.
Removing them caused field 637 to lose CSR changes the human had verified
were present before. **Reverted** in the same-day follow-up commit —
`single-disc-on-csr/layers/disc1.layer.json` is restored to its
pre-2026-08-18 state (all 414665 records).

The apply-order fix in `scripts/build_with_website_code.js` (manip-movies →
single-disc-on-csr → parts 2-10 → endings parts 1-7) was correct and kept.

## Original (retracted) theory, for reference

`single-disc-csr-manip-movies-v0.1.4` writes MOVIE_ID rows 47
(JAIROFAL/LOSLAKE1) and 52 (CAR_1209/Hojo CANONHT2) with Form2 engine length
(`nsec*2336`). It was believed `single-disc-on-csr` reverted this:

| Row | Field | Manip-movies | on-csr (believed to overwrite) |
|-----|-------|------------------------|------------------------|
| 47 | size | 17190624 (Form2) | 31848448 |
| 52 | size | 5977824 (Form2) | 6027488 |

This table's premise — that the on-csr values are wrong and the manip-movies
values are the correct Form2 target — has not been independently confirmed
against a genuinely flicker-free reference. Do not reuse this diagnosis
without first establishing a real known-good baseline (e.g. deriving the
correct Form2 length from the source FMV's actual sector count, not from any
existing disc image).

## Not fixed

The actual LOSLAKE1/Hojo/ending audio flicker root cause is still unknown
and unfixed. Next step: derive correct Form2 `nsec*2336` engine lengths from
first principles (real FMV file/sector sizes) rather than by diffing against
any existing built disc image, since none confirmed so far are flicker-free.

The ENDING2E.MOV LBA-collision corruption (documented separately — ending
movie clobbers ~13 other movies' sectors) is a distinct, unrelated bug from
this audio-only flicker. Not touched by this change.
