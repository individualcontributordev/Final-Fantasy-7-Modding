# CSR movie-id sorted-directory bug + full CFG reachability scan results

**Date:** 2026-08-24
**Confidence:** confirmed
**Status:** open
**Related:** docs/findings/2026-08-07-csr-d3-ending-movie-jumps.md, docs/findings/2026-08-19-fresh-field-collision-scan.md, mods/single-disc/patches/csr-manip-movie-seed.txt

## Summary

Built a CFG-based (not opcode-presence) PMVIE/MOVIE reachability analyzer,
validated it against three known CSR skip findings, then used it to scan
CSR D1/D2/D3 for every field's *actually reachable* movie. Found a
disc-local-id resolution bug in our own prior tooling along the way:
PMVIE id is NOT "sorted MOVIE/ directory order" — it's the row index into
that disc's own `MINT/MOVIE_ID.BIN` table (`row[id].lba` -> dirent lookup
by LBA). `inject_movies_by_disc_id.py`'s docstring/comments describe the
sorted-dir-order model, but its manifest entries were all hand-verified
explicit names, so it never actually produced a wrong result in practice.
Two new one-off scan scripts (analyze_movie_reachability.py,
scan_csr_movie_reachability.py, scan_sd_movie_requirements.py) briefly
had the same wrong assumption; fixed in the same session before any output
was trusted or shipped.

## Context

User wants CANONON (locked to LOSLAKE1's hardcoded LBA 250450 seek) moved
out of the way of the D3 ending movies at EOF, plus "a few other movie
files" they found that need relocating from D2 to D1. Established
(previous session) that CANONON cannot be relocated — no dirent, hardware
seek — so ENDING2E must be routed around it instead. Before doing that,
needed the full picture: which D2/D3 movies does CSR's *actual* (reachable,
not skipped) field-script logic require on the single-disc build, so all
placements/relocations can be planned together instead of one collision at
a time.

## Discovery

### Bug: PMVIE id resolution

```
CSR D2 MOVIE_ID.BIN row 0: lba=129252 -> dirent lookup -> FSHIP2.BIN
Sorted MOVIE/ directory index 0 (alphabetical): BOOGDOWN.STR (lba=137289)
```

Every one of 61 D2 rows mismatched between "table order" and "sorted dir
order" when checked side by side. Correct resolution:
`MOVIE_ID.BIN[id].lba` -> find the MOVIE/ dirent whose LBA equals that ->
that dirent's filename is the PMVIE-id-N movie for that disc.

### CFG reachability analyzer

`mods/single-disc/scripts/analyze_movie_reachability.py` does real
control-flow BFS from each script slot's offset 0, using the same
JUMP_INFO jump-math table as `remove_dskcg.py` (JMPF/JMPFL/JMPB/JMPBL
unconditional -> jump edge only; IFxx family conditional -> jump + fallthrough
edges; RET/RETTO/GAMEOVER -> no fallthrough).

Validated against 3 known cases, all matched exactly:
- CSR D3 LAS4_0: PMVIE 25 (ENDING01) unreachable (JMPF skips it) — matches
  2026-08-07 finding.
- CSR D3 LASTMAP AD3/31: early JMPF skips the REQ->AD3 block queuing
  PMVIE 23 — matches 2026-08-07 finding.
- CSR D3 LASTMAP AD/31: MOVIE op unreachable (sits after unconditional RET,
  no back-edge) — matches 2026-08-07 finding (our own NOP fix, separate
  from CSR).
- CSR D2 LOSLAKE1 cl/31: PMVIE 47 (CANONON.MOV) reachable — matches known
  behavior.

### 82 tiny placeholder fields (all 3 discs)

BLACKBGA, FALLP, TRAP, M_ENDO, etc. — FIELD/*.DAT decompress to 36 bytes,
no real script content, same 82 names across D1/D2/D3. Harmless parse
"errors" in the scan (not real fields), confirmed benign.

### Full-disc reachability counts (post-fix)

- D1: 58 movies reachable from >=1 field, 2 referenced-but-dead
- D2: 57 movies reachable from >=1 field, 3 referenced-but-dead
- D3: 58 movies reachable from >=1 field, 2 referenced-but-dead
- CSR D2 MOVIE_ID.BIN: 61 rows. CSR D3: 30 rows. Built single-disc D1
  currently: only 54 rows — smaller than D2's table, so D2 ids 54 and 60
  have no corresponding D1 row at all (need table growth, not just a
  repoint).

### Movies the current single-disc build's *reachable* CSR field logic
needs but doesn't yet have correctly wired on D1 (17 real mismatches,
2 separate OOB-id cases needing table growth)

| Field | Entity/slot | id | Origin | Needs (movie) | Currently at that D1 id |
|---|---|---|---|---|---|
| LOSLAKE1 | cl/31 | 47 | D2 | CANONON.MOV | JAIROFAL.MOV (already tracked, seed file line 8) |
| LAS4_2 | batkun/31 | 20 | D3 | LAST4_2.BIN | MKUP.STR (NOT in seed file yet — gap) |
| LAS4_3 | batkun/31 | 21 | D3 | LAST4_3.BIN | NORTHMK.MOV (in seed file already) |
| CONVIL_2 | event/31 | 33 | D2 | PHOENIX.MOV | BRGNVL.MOV |
| JUNAIR | glin/3 | 40 | D2 | GELNICA.MOV | GOLD1.MOV |
| JUNONE7 | dir/31 | 32 | D2 | HWINDFLY.MOV | MTNVL2.STR |
| RCKTIN5 | cid/13 | 41 | D2 | RCKTOFF.MOV | BISKDEAD.STR |
| RCKTIN7 | space/31 | 45 | D2 | RCKTHIT2.MOV | RCKTFAIL.MOV |
| RCKTIN7 | siera/3 | 44 | D2 | RCKTHIT.MOV | SETO.STR |
| TRNAD_51 | tg_d/31 | 23 | D2 | C_SCENE3.MOV | ONTRAIN.MOV |
| TRNAD_51 | tg_d/31 | 21 | D2 | C_SCENE1.MOV | NORTHMK.MOV |
| TRNAD_51 | tg_d/31 | 24 | D2 | FF_DAIKU.MOV | MAINPLR.MOV |
| TRNAD_52 | t_dirct/31 | 22 | D2 | C_SCENE2.MOV | MK8.STR |
| ZCOAL_3 | cid/31 | 34 | D2 | NRCRL.MOV | NVLMK.MOV |
| ZMIND2 | shad3/31 | 38 | D2 | ZMIND21.STR | HIWIND0.MOV |
| BLIN70_4 | event/2 | 60 | D2 | CANON.MOV (23.2 MB) | **no D1 row (OOB)** |
| FSHIP_2 | direct/31 | 54 | D2 | HWINDJET.MOV (5.55 MB) | **no D1 row (OOB)** |

Sizes for the largest new-content items (D2 source, full Form2 sectors):
FF_DAIKU.MOV 22.8 MB, CANON.MOV 23.2 MB, RCKTOFF.MOV 17.0 MB,
HWINDFLY.MOV 16.2 MB, CANONON.MOV 14.4 MB (already placed), RCKTHIT2.MOV
9.2 MB, PHOENIX.MOV 8.3 MB (referenced by CONVIL_2, not the OOB BLIN70_4
row), HWINDJET.MOV 5.6 MB, RCKTHIT.MOV 5.7 MB, NRCRL.MOV 5.5 MB, GELNICA.MOV
6.1 MB, ZMIND21.STR 2.6 MB, C_SCENE1/2/3.MOV ~5 MB each.

Current single-disc-core free budget (from `build_singledisc_core_bin.py`
output): 318,357 sectors used of 360,000 (80-min budget) = 41,643 sectors
(~93.4 MB) free. The candidate new-content list above (excluding items
already resolvable by a same-slot swap) totals roughly 90+ MB if all
taken as new EOF additions — tight against the 93 MB headroom and doesn't
yet account for the ENDING2E/GOLD7_2/CANONON relocation space already
consumed by `alias_d3_ending_lbas_on_d1.py`.

## How we found it

1. Re-derived JUMP_INFO edge semantics from `remove_dskcg.py` (already
   verified against Makou Reactor's Opcode.h).
2. Wrote `analyze_movie_reachability.py`, validated against 3 known
   findings (CLI: `python3 mods/single-disc/scripts/analyze_movie_reachability.py --disc csr:3 --field LAS4_0` etc.) — all matched.
3. Wrote `scan_csr_movie_reachability.py` to run the analyzer over every
   FIELD/*.DAT on CSR D1/D2/D3, initially resolving PMVIE ids via sorted
   MOVIE/ directory order (copied the (buggy) assumption from
   `inject_movies_by_disc_id.py`'s docstring).
4. First-pass results contained nonsense hits (`GDUMMY1.HTM`, `DISK1.LZS`,
   `CHANGE4.LZS` as "intended movies" for real cutscene fields) — smell
   test failed, investigated by diffing MOVIE_ID.BIN row order vs sorted
   dir order side by side (see Discovery). Confirmed 100% mismatch rate
   between the two orderings across all 61 D2 rows.
5. Fixed both scan scripts to resolve via `MOVIE_ID.BIN[id].lba -> dirent`
   instead. Re-ran; results now sane (LAS4_2/LAS4_3/LOSLAKE1 hits line up
   with already-known seed-file entries).
6. Wrote `scan_sd_movie_requirements.py` to cross-reference the built
   `ff7_d1_singledisc_core.bin` (fields already chosen per CSR/pristine
   preference) against origin-disc reachability + origin-disc MOVIE_ID
   table, producing the mismatch table above.

## Why it matters

- Any future scan/injection tooling that assumes "sorted MOVIE/ dir order
  = PMVIE id" will silently target the wrong movie. `inject_movies_by_disc_id.py`
  itself wasn't actually bitten (manifest lines are explicit/hand-verified),
  but its docstring is misleading and should not be used as a template for
  new automated resolution.
- The reachability analyzer is now validated tooling — safe to reuse for
  future CSR-skip audits instead of manual Ghidra/manip-movie tracing.
- The 17-mismatch + 2-OOB list is the first complete (not spot-checked)
  picture of what CSR's live D1 single-disc build actually needs movie-wise.
  LAS4_2/LAST4_2.BIN is a **new gap** not previously in
  `csr-manip-movie-seed.txt` (LAS4_3/LASTMAP were already there).
  The two OOB ids (BLIN70_4/id60, FSHIP_2/id54) need D1's MOVIE_ID.BIN
  table extended past its current 54 rows before they can be aliased at
  all — a new class of problem beyond simple slot-repoint.

## Update 2026-08-24 (later): build_playtest_bin.py only applied v0.1.5, skipped v0.1.4

While validating the CANONON/ENDING2E fix, `build_ending_credits_test_bin.py`
(which calls `build_playtest_bin.py`) failed with "movies layer did not
install CANONON into JAIROFAL." Root cause: `build_playtest_bin.py` only
applied the `single-disc-csr-manip-movies-v0.1.5` layer. v0.1.5 is a
**delta pack** — its stored diff (`originalBytes: 766340400`) is computed
against v0.1.4's *output*, not against the single-disc core layer's output
(748775664 bytes). Applying v0.1.5 directly onto the core silently patches
bytes at offsets that don't correspond to what v0.1.5 intended (no error —
`apply_layer` just writes at whatever offsets the diff specifies), leaving
JAIROFAL == vanilla D1 instead of CANONON.

Confirmed by manually replaying `apply_layer` step by step: core -> v0.1.4
-> v0.1.5 gives JAIROFAL == CANONON (correct); core -> v0.1.5 alone does
not. `builder/manifest.json`'s own blurb for v0.1.5 already documented this
("applies after manip-movies v0.1.4") — the build script just didn't follow
it.

**Fix:** `build_playtest_bin.py` now applies v0.1.4 then v0.1.5 in order
(4 steps total instead of 3). Re-verified full ending-credits chain after
the fix:

- JAIROFAL == D2 CANONON (bit-exact)
- ISO LBA 250450 sector0 == D2 CANONON sector0, submode 0x42 (Form2)
- `alias_d3_ending_lbas_on_d1.py` relocates GOLD7_2.MOV to EOF LBA 336392
  before writing ENDING2E (collision-safe)
- CANONON re-punched at LBA 250450 after ENDING2E write (known-good v7
  fix from `docs/findings/2026-08-07-ending-credits-test-inject.md`) —
  confirmed bit-exact against D2 CANONON post-punch
- GOLD7_2.MOV (relocated slot) == D3 LAST4_3.BIN (bit-exact)
- Final image: 791,483,280 bytes / 336,515 sectors, 23,485 sectors
  (~44 MiB) free of the 360,000-sector 80-min budget

Built `workspace/iso-extract/ff7_d1_playtest_ending_test.bin` +
`.cue` — ready for a DuckStation playtest of the ending sequence with
manip-movies + CANONON/LOSLAKE1 both present.

## Follow-ups

- [ ] Decide relocation target for CANONON's *collision* (ENDING2E must be
      routed around LBA 250450, not CANONON moved) — separate task already
      in progress this session.
- [ ] Add LAS4_2/LAST4_2.BIN to csr-manip-movie-seed.txt (currently missing).
- [ ] Design MOVIE_ID.BIN row-table growth (54 -> at least 61 rows) to
      support BLIN70_4/id60 and FSHIP_2/id54, or confirm those two fields'
      PMVIE calls are otherwise unreachable/skippable on the single-disc
      build (would need per-field CSR-D1-script check, not yet done for
      fields whose FIELD/*.DAT origin is D1 already).
- [ ] Budget check: sum exact EOF-append bytes needed for all real new
      content (excluding same-slot swaps) against remaining ~93 MB before
      committing to placing everything.
- [ ] Verify entity/slot names ("cl", "batkun", "tg_d", etc.) against
      Makou Reactor's per-field entity list for a couple of fields as a
      sanity spot-check (not done yet, decode_field_script.py's entity
      naming assumed correct from field_dat.py without independent check
      this session).

## Sources

- `mods/single-disc/scripts/analyze_movie_reachability.py`
- `mods/single-disc/scripts/scan_csr_movie_reachability.py`
- `mods/single-disc/scripts/scan_sd_movie_requirements.py`
- `mods/single-disc/scripts/remove_dskcg.py` (JUMP_INFO source of truth)
- `/tmp/csr_movie_reachability.json`, `/tmp/sd_movie_requirements.json`
  (not committed — regenerate via the scripts above)
