# CANONON/ENDING "hardcoded LBA" theory — clean-room re-verification

**Date:** 2026-08-24
**Confidence:** confirmed (source + byte-level + live single-variable test)
**Status:** confirmed
**Related:** the live test below reconfirms the "hardcoded LBA" conclusion
originally reached in `2026-08-07-ending-credits-test-inject.md` and
`2026-08-07-csr-d3-ending-movie-jumps.md`, this time with a clean
single-variable methodology rather than the original confounded test.

## Summary

Independently re-derived, from raw bytes and Makou Reactor source only (no
reliance on prior findings), that `PMVIE` is a disc-agnostic 1-byte movie ID
with no embedded LBA anywhere in the opcode, field script, or `FIELD.BIN`/
`BATTLE.X`. This ruled out the field script / opcode as the source of any
hardcode, but left open whether the engine itself still honors
`MOVIE_ID.BIN` at runtime for this specific id. A clean single-variable live
test (pristine Disc 2, only `MOVIE_ID.BIN` row 47 changed) now confirms it
does **not**: the engine seeks LBA 250450 directly for id 47, ignoring the
table entirely, even on the disc the table was authored for.

## Context

Prior notes (2026-08-07) claimed growing `MOVIE_ID` row 25 didn't change the
ending movie's seek in a DuckStation trace, concluding CANONON/ENDING use a
hardcoded absolute LBA seek instead of the table, causing an LBA-aliasing
strategy with a known ENDING2E/CANONON overlap glitch. User asked for
clean-room re-verification since that conclusion could be an agent
hallucination.

## Discovery

**1. Field script bytecode (raw bytes, evidence class: bytes)**
- `FIELD/LOSLAKE1.DAT` (D2): `PMVIE` opcode = `f8 2f` → 1-byte id 47.
- `FIELD/LAS4_0.DAT` (D3): `PMVIE` opcode = `f8 19` → 1-byte id 25.
- A 1-byte field cannot embed a 32-bit LBA — the field script itself is not
  the source of any hardcode.

**2. `SCUS_941.63` raw scan (evidence class: bytes)**
- Scanned for LBAs 163608 / 172631 / 197242 / 250450 as 32-bit LE words and
  as BCD MSF triples (both byte orders). Zero static hits for any of them.

**3. `MOVIE_ID.BIN` table (evidence class: bytes)**
- D2 row 47 = LBA 250450, matches `CANONON.MOV` — consistent with prior
  notes' number (not invented), but only proves the *table* is
  self-consistent, not that the engine reads it for this ID.

**4. Makou Reactor source (evidence class: source code)**
- `src/core/field/Opcode.h:1497-1501`:
  ```cpp
  STRUCTPACK(struct OpcodeMovie : public OpcodeBase { quint8 movieID; });
  STRUCTPACK(struct OpcodePMVIE : public OpcodeMovie {});
  ```
  Confirms opcode is exactly one byte, no LBA field.
- `src/widgets/ScriptEditorWidgets/ScriptEditorMoviePage.cpp:82-89`
  (`buildOpcode()`): the UI's "Disc" combo box is **never read** when
  writing the opcode — only `movieList->currentIndex()` (0-255) is stored.
- `src/widgets/ScriptEditorWidgets/ScriptEditorMoviePage.cpp:61-80`
  (`setMovieListItemTexts()`): the disc combo only swaps which
  `Data::movie_names_cd1/cd2/cd3` string list labels the dropdown — cosmetic
  relabeling only, not a data path.
- `src/Data.cpp:607-623` (`movieList[106]`) + `:526-544` (list-building
  loop): confirms per-disc ID ranges are common[0-19] + disc-specific
  slice, not per-opcode LBA storage.

**5. Cross-check — 3 independent sources agree (evidence class: bytes +
source, cross-referenced)**
- D2: `movieList[81]` = `"canonon"` → cd2-list index = 20+(81-54) = **47**.
  Matches `LOSLAKE1.DAT`'s `f8 2f` (47) and `MOVIE_ID.BIN` row 47.
- D3: `movieList[101]` = `"ending1"` → cd3-list index = 20+(101-96) = **25**.
  Matches `LAS4_0.DAT`'s `f8 19` (25).

## How we found it

Manual bytecode decode of the two field scripts, raw hex scan of the
executable for candidate LBA literals (both encodings), direct read of
Makou Reactor 2.1.0 C++ source (`Opcode.h`, `Opcode.cpp`,
`ScriptEditorMoviePage.cpp/.h`, `Data.cpp`) cloned at
`workspace/makoureactor`.

## Why it matters

If the engine actually does honor `MOVIE_ID.BIN` for CANONON/ENDING (pending
live test), the LBA-aliasing workaround and its known overlap glitch become
unnecessary — these could ship as ordinary table entries like the other 17
reachable movies already handled by `inject_movies_by_disc_id.py`.

## Live test result (2026-08-24, user-run on Windows/Git Bash)

Built a pristine-Disc-2 copy with **only** `MINT/MOVIE_ID.BIN` row 47
rewritten (LBA 250450 `CANONON.MOV` → LBA 136669 `BOOGUP.STR`, a visually
distinct snowboard clip). No file moves, no size changes, no field-script
edits — single byte-range change only (see `docs/INSTRUCTIONS.md`).

**Result: the real CANONON cannon movie played, unaffected by the patch.**
The snowboard clip never appeared. This confirms the engine seeks LBA
250450 directly for PMVIE id 47 on `LOSLAKE1`, regardless of what
`MOVIE_ID.BIN` row 47 contains — even on genuine Disc 2, not just the
single-disc D1 rebuild. The "hardcoded LBA" theory is confirmed, not
overturned.

## Follow-ups

- [x] Run the live single-variable test in `docs/INSTRUCTIONS.md` — done,
      table ignored, hardcoded LBA confirmed.
- [x] Engine ignores the table for CANONON: the LBA-aliasing approach
      (`alias_d2_seek_lba_on_d1.py`, hardcoded LBA 250450) remains
      necessary for this movie; it cannot be folded into the standard
      `MOVIE_ID.BIN`-only seed-file mechanism.
- [ ] Still open: whether this hardcoded-seek behavior is unique to
      CANONON/id 47, or affects other PMVIE ids too. Only id 47 has been
      live-tested; the 17-movie relocation to-do list still assumes the
      table path works for every other id, unproven either way. A Ghidra
      disassembly of the field movie-play routine (search for LBA 250450 /
      MSF-encoded literal, or the code path branching around the
      `MOVIE_ID.BIN` read) could identify whether this is a one-off
      special case or a broader pattern before relying on the assumption
      for the remaining movies.

## Sources

- `workspace/makoureactor/src/core/field/Opcode.h` (lines 1497-1501)
- `workspace/makoureactor/src/core/field/Opcode.cpp` (lines 4876-4881,
  5011-5026, 5567, 5843)
- `workspace/makoureactor/src/widgets/ScriptEditorWidgets/ScriptEditorMoviePage.cpp`
  (lines 26-99)
- `workspace/makoureactor/src/Data.cpp` (lines 526-544, 607-623)
- `docs/reference/movie-id-mapping.txt`, `docs/reference/INDEX.md`
- `docs/INSTRUCTIONS.md` (pending live test)
