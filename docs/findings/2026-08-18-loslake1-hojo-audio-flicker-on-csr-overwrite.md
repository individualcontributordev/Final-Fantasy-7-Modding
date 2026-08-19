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

## 2026-08-19 update: first-principles Form2 lengths derived

Human reported field 643 (WHITE2) CSR changes missing and field 637 flicker
still present after the revert. Diffed the **live CDN** copy of
`single-disc-on-csr/layers/disc1.layer.json` byte-for-byte against the repo
(`cc21763`): identical, 414,665 records, field 643/637 bytes both present.
Conclusion: the report was a stale client cache (IndexedDB), not a content
regression — the "clear pack cache" button was likely clicked before GitHub
Pages finished publishing. Retest requested via incognito window to rule
this out definitively.

Also derived correct Form2 MOVIE_ID engine lengths (`nsec*2336` where
`nsec = ceil(iso_size / 2048)`) directly from each FMV's real ISO directory
size on pristine Disc 2 — not from any existing built disc image:

| Movie | Field | ISO size (D2) | nsec | Correct Form2 (nsec*2336) | Current manip-movies value |
|-------|-------|---------------:|-----:|---------------------------:|----------------------------:|
| CANONHT2.MOV | 637 (Hojo) | 5,240,832 | 2559 | 5,977,824 | 5,977,824 (matches) |
| LOSLAKE1.MOV | Bugenhagen waterfall | 6,060,032 | 2959 | 6,912,224 | 17,190,624 (wrong) |

Row 52 (Hojo/CANONHT2) already carries the mathematically-correct Form2
value, so that movie should already be flicker-free — worth confirming
independently in the retest. Row 47 (LOSLAKE1) is written with 17,190,624,
which is not even a multiple of 2336, so it cannot be a valid Form2 length;
this is the leading suspect for the still-present LOSLAKE1 flicker. Not
changed yet — waiting on the incognito retest for a clean before/after
before touching `single-disc-csr-manip-movies-v0.1.4`.

## 2026-08-19 update: field↔movie mapping was wrong (row index ≠ movie ID)

Human clarified field 637 (internal field name `loslake1`) actually plays a
**cannon** scene, not the waterfall — the waterfall (`LOSLAKE1.MOV`) plays
elsewhere. This exposed a second derivation error: I had picked
`MOVIE_ID.BIN` rows 47/52 by sorting the ISO `MOVIE/` directory
alphabetically, but rows are indexed by the **`PMVIE` opcode's movie ID**,
which follows internal build order, not alphabetical filename order.

Decoded the actual `PMVIE` opcodes from field scripts on the CSR base
(`scripts/field_dat.py` + `ff7_opcodes.py`, cross-checked against Makou
Reactor's `Opcode.cpp`/`Data.cpp`):

| Field (ID / internal name) | PMVIE id(s) called | Resolves to (via D2 `MINT/MOVIE_ID.BIN` row order) |
|---|---|---|
| 637 `loslake1` | 47 | `CANONON.MOV` (cannon scene — matches human's report) |
| 639 `loslake3` | 57 | `LOSLAKE1.MOV` (the actual waterfall FMV) |
| 643 `white2` | 28, 42, 56 | `WEAPON2.MOV`, `WHITE2.BIN`, `C_SCENE2.MOV` — **not** LOSLAKE1 |

So field 639, not 643, appears to be the field that actually plays the
waterfall movie. Field 643 doesn't reference `LOSLAKE1.MOV` at all in the
CSR base. Also note: earlier `docs/reference/movie-id-mapping.txt` (global
movie-ID concat: common 0–19, disc1 20–53, disc2 54–95, disc3 96–105) uses
a **different index space** than PMVIE's per-disc-local row order used by
`MINT/MOVIE_ID.BIN` — row 47 in that global table is `jairofal`, but PMVIE
id 47 on disc 2 is `CANONON.MOV`. Do not cross-reference the two tables
directly.

Re-derived `LOSLAKE1.MOV`'s Form2 engine length by reading Disc 2's own
`MINT/MOVIE_ID.BIN` row directly (`_movie_id_meta_by_lba` in
`mods/single-disc/scripts/inject_movies_by_disc_id.py`) instead of
computing `nsec*2336` from the ISO size — this is strictly more reliable
since it copies the disc's own aux fields too:

- `LOSLAKE1.MOV` on D2: lba 291219, ISO size 6,060,032, MOVIE_ID row =
  (size=6,912,224, aux=(0, 0x00FFFFFF, 235)). Matches the previously
  computed `nsec*2336` value exactly.
- `CANONHT2.MOV` on D2: lba 268006, ISO size 5,240,832, MOVIE_ID row =
  (size=5,977,824, aux=(0, 0x00D01050, 206)) — also matches.

**Still unconfirmed:** which field number the human actually sees when
watching the waterfall/Aeris-face scene (639 vs. 643 vs. something else).
`docs/INSTRUCTIONS.md` asks for this before any `MOVIE_ID.BIN` edit, so the
fix targets the correct row this time.
