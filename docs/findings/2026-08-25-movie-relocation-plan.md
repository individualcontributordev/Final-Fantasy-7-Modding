LIMIT THE FILE CONTENT TO AT MOST 150 LINES. IF MORE CONTENT NEEDS TO BE ADDED USE THE str-replace-editor TOOL TO EDIT THE FILE AFTER IT HAS BEEN CREATED.
# Single-disc movie relocation plan (re-verified, narrowed from 17 to 4 sites)

**Date:** 2026-08-25
**Confidence:** confirmed (re-verified against current tooling + built core.bin)
**Status:** open
**Related:** docs/findings/2026-08-24-csr-movie-reachability-scan.md (superseded numbers), docs/findings/2026-08-25-fship22-fship25-movie-unresolved.md, mods/single-disc/patches/csr-manip-movie-seed.txt

## Summary

Re-ran `scan_csr_movie_reachability.py` + `scan_sd_movie_requirements.py`
against the current built `ff7_d1_singledisc_core.bin` and CSR sources.
The 2026-08-24 finding's "17 mismatches + 2 OOB" list is **stale** — most
of those rows have `slot_live=False` (the calling entity/slot is never
actually invoked, confirmed by the `compute_slot_liveness` REQ/PREQ
call-graph added after that finding). Filtering to `slot_live=True` only,
the real remaining gap is **4 movie-id conflicts across 3 fields**, one of
which (LOSLAKE1/CANONON) is already shipped.

## Context

Task: "propose relocation/dirent-reuse plan" for single-disc D1 movies
CSR's D2/D3 field scripts actually need. Before drafting the plan, user
asked to re-verify the 08-24 mismatch list is still current, since
`live`-aware filtering and the `field_dat.py` extractor fix landed since
then.

## Discovery

### Re-run results (current)

```
python3 mods/single-disc/scripts/scan_csr_movie_reachability.py
  D1: 20 required, D2: 17 required, D3: 20 required (unchanged from 08-24)

python3 mods/single-disc/scripts/scan_sd_movie_requirements.py \
  --bin workspace/iso-extract/ff7_d1_singledisc_core.bin
  475 reachable MOVIE-call resolutions; 142 raw mismatches;
  14 of those have slot_live=True (the rest are orphan/uncalled slots,
  same UNRESOLVED-category pattern as FSHIP_22/25 and the 82 placeholder
  fields — not real requirements)
```

### The 4 real live-mismatch sites

| Field | Entity/slot | id | Origin | Needs | Currently at D1 id | Any other live user of current content? |
|---|---|---|---|---|---|---|
| LOSLAKE1 | cl/9 | 47 | D2 | CANONON.MOV | JAIROFAL.MOV | **Already shipped** (csr-manip-movie-seed.txt line 8, `alias_d2_seek_lba_on_d1.py` for the hardcoded LBA 250450 seek) |
| JUNAIR | glin/3 | 40 | D2 | GELNICA.MOV (6.11 MB) | GOLD1.MOV | No live user found for GOLD1.MOV content at id 40 |
| TRNAD_51 | tg_d/4,5,6,7 | 21 | D2 | C_SCENE1.MOV (5.28 MB) | NORTHMK.MOV | No live user found for NORTHMK.MOV at id 21 |
| TRNAD_51 | tg_d/4,5,6,7 | 23 | D2 | C_SCENE3.MOV (4.87 MB) | ONTRAIN.MOV | No live user found for ONTRAIN.MOV at id 23 |
| TRNAD_51 | tg_d/4,5,6,7 | 24 | D2 | FF_DAIKU.MOV (22.81 MB) | MAINPLR.MOV | **Yes** — `ROOTMAP/direct/1` (pristine D1 origin) is a live, non-mismatched reader of id 24 = MAINPLR.MOV |

TRNAD_51 slots 4/5/6/7 all resolve the same 3 ids — same script content
repeated per some game-state branch (multi-disc "next movie" style
duplication), not 4 independent requirements.

### The id-24 conflict (only real collision)

`ROOTMAP/direct/1` needs the *current* D1 id-24 content (MAINPLR.MOV)
to keep playing, while `TRNAD_51/tg_d` needs id 24 to become
FF_DAIKU.MOV. Cannot repoint id 24 in place — must either:
- give FF_DAIKU.MOV a **new** MOVIE_ID.BIN row (id 54, next free index —
  D1 table currently has 54 rows, ids 0-53) and repoint `TRNAD_51/tg_d`'s
  `PMVIE` operand from 24 to 54, or
- move MAINPLR.MOV's *content* to a different id and repoint ROOTMAP's
  PMVIE operand instead.

The first option (grow the table by 1, point the new id at newly-appended
FF_DAIKU.MOV bytes) avoids touching ROOTMAP's script at all — lower risk.
This *is* the same "MOVIE_ID.BIN row-table growth" mechanism the 08-24
finding flagged as needed for BLIN70_4/FSHIP_2 (ids 60/54) — those two
turned out to be `slot_live=False` (not real requirements) on re-check,
but the growth mechanism itself is still needed here for FF_DAIKU.MOV.

### EOF budget

Built core.bin: 748,775,664 bytes = ~318,357 sectors of the 360,000
(80-min) budget → ~41,643 sectors (~81.3 MB) free.

New content needed (GELNICA + C_SCENE1 + C_SCENE3 + FF_DAIKU, appended
once, Form2 2048-byte sectors): 20,005 sectors (~39.1 MB). Comfortably
fits in the ~81 MB headroom even before considering any same-slot
repoints that need no new space at all.

## How we found it

1. Re-ran both scan scripts fresh against current CSR sources and the
   existing built `ff7_d1_singledisc_core.bin` (confirmed the
   `field_dat.py` split-script fix is additive and doesn't change
   `ScriptSlot.slot` numbering these scripts key off — no rebuild needed
   before re-scanning).
2. Filtered `scan_sd_movie_requirements.py` output to `slot_live=True`
   rows only — this is the same liveness signal already validated
   against FSHIP_22/23/25 and BLIN2_I in the previous session.
3. Cross-checked whether any *other* live row currently depends on the
   content sitting at each target id (ids 21/23/24/40/47) before treating
   a repoint as collision-free — found the ROOTMAP/id-24 conflict this
   way; ids 21/23/40 have no other live reader.
4. Pulled exact Form2 byte sizes for the 4 needed movies from CSR D2's
   MOVIE/ directory and computed sector counts against the built core's
   remaining 80-min budget.

## Why it matters

The 08-24 finding's headline "17 mismatches + 2 OOB, ~90 MB, tight
against 93 MB headroom" was overly pessimistic — most of those 17 rows
were never-called script slots, not real gameplay-visible requirements.
The real scope is 3 repoints (no new space) + 1 table-growth append
(~22.8 MB of the ~39 MB total) — well inside budget, no collision with
already-shipped LOSLAKE1/CANONON or the ENDING2E/GOLD7_2 EOF relocation.

## Follow-ups

- [ ] Implement: repoint D1 MOVIE_ID.BIN id 21 → C_SCENE1.MOV bytes,
      id 23 → C_SCENE3.MOV bytes (same-slot swap, no dirent/table change).
- [ ] Implement: repoint D1 MOVIE_ID.BIN id 40 → GELNICA.MOV bytes
      (same-slot swap).
- [ ] Implement: grow D1 MOVIE_ID.BIN to 55 rows, append FF_DAIKU.MOV at
      EOF, add row 54 pointing at it, and patch `TRNAD_51/tg_d` slots
      4/5/6/7's `PMVIE` operand from 24 to 54 (leaves ROOTMAP untouched).
- [ ] Verify table-growth mechanism (row format, dirent creation) against
      an existing example before writing the patch script — no prior
      single-disc mod has grown this table yet.
- [ ] Playtest JUNAIR (Gelnica), TRNAD_51 (all 4 slot variants), and
      confirm ROOTMAP's MAINPLR.MOV playback is unaffected.

## Sources

- `mods/single-disc/scripts/scan_csr_movie_reachability.py`
- `mods/single-disc/scripts/scan_sd_movie_requirements.py`
- `workspace/iso-extract/ff7_d1_singledisc_core.bin`
- `/tmp/csr_movie_reach_verify.json`, `/tmp/sd_movie_requirements_verify.json`
  (not committed — regenerate via the scripts above)
