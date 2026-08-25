LIMIT THE FILE CONTENT TO AT MOST 150 LINES. IF MORE CONTENT NEEDS TO BE ADDED USE THE str-replace-editor TOOL TO EDIT THE FILE AFTER IT HAS BEEN CREATED.
# FSHIP_22/FSHIP_25 orphan MOVIE calls trace (CSR D3) — UNRESOLVED, not required

**Date:** 2026-08-25
**Confidence:** confirmed
**Status:** open
**Related:** docs/findings/2026-08-24-csr-movie-reachability-scan.md, docs/findings/2026-08-24-field-bin-pmvie-movie-mvief-handlers-located.md

## Summary

`FSHIP_22` (field id 69, entity `mov`/slot 1) and `FSHIP_25` (field id 72,
entity `move`/slot 1) both contain a bare `MOVIE` opcode with no local
`PMVIE` setter, and their only live callers into the field also lack any
`PMVIE`/`BGMOVIE`. Both are UNRESOLVED-category orphan movie calls (same
bucket as the other 7 already-catalogued sites), not new required-movie
sites for the single-disc movie relocation plan.

## Context

Part of the 17-problem-site single-disc movie relocation audit (8 vanilla
dead-code branches already resolved, 9 UNRESOLVED sites being traced one
at a time). Needed to confirm whether FSHIP_22/FSHIP_25's `MOVIE` calls
resolve to a real, disc-required movie ID via any traceable caller chain,
using the now-fixed `split_script_at_return`-aware field extractor.

## Discovery

CSR D3, via `analyze_field_bytes()` (mods/single-disc/scripts/analyze_movie_reachability.py):

```
FSHIP_22 (field id 69):
  mov/0   : RET; RET                      (dead, live=False downstream slots)
  mov/1   : MOVIE f9; RET                 (live=True, no local PMVIE)
  Only live caller: TRNAD_2 / hikutei / slot 2
    IFUB -> UC -> MENU2 -> BITON -> REQEW -> WAIT -> MAPJUMP(->FSHIP_22)
    No PMVIE/BGMOVIE anywhere in this caller script either.

FSHIP_25 (field id 72):
  move/1  : MOVIE f9; RET                 (live=True, no local PMVIE)
  Only live caller: CANON_2 / hojyo / slot 1
    Full Hojyo cable-car battle setup/dialogue script (BATTLE -> FADE ->
    dialogue chain -> MAPJUMP(->FSHIP_25)). No PMVIE/BGMOVIE anywhere.
```

Both `direct`/`mov` slot-0 physical scripts for FSHIP_22 confirmed
byte-identical to slot-1 for the `direct` entity (both live, both begin
with `RET` at offset 0 — Init/Main split degenerate here since slot 0 is
`S0-Init` = single leading `RET`, slot 1 is the raw physical blob's
continuation, per the `split_script_at_return` fix). `mov` entity has
slots 0 (dead `RET;RET`) and 1 (the live `MOVIE;RET` pair) as genuinely
distinct physical scripts, not an Init/Main split artifact.

Field-id lookups used `docs/reference/field-id-mapping.txt`:
FSHIP_22 = id 69, FSHIP_25 = id 72.

## How we found it

1. `scan_csr_movie_reachability.build_field_graph()` reverse-lookup: swept
   every CSR D3 field's `reachable_mapjump_targets()` for edges into field
   ids 69/72, collecting `(caller_field, entity, slot, live)` tuples.
2. Found live callers: `TRNAD_2/hikutei/2` -> FSHIP_22, and
   `CANON_2/hojyo/{1,2,3,5}` (+ `BLACKBG5`, `FSHIP_3`, `FSHIP_4` — excluded
   as noise/non-primary per `MAPJUMP_FANOUT_EXCLUDE` reasoning) -> FSHIP_25.
3. Dumped full opcode listing for `TRNAD_2/hikutei/2` and `CANON_2/hojyo/1`
   via `fmt_op()` — manually scanned for `PMVIE` (0xf8) or `BGMOVIE`;
   neither present in either caller.
4. Dumped FSHIP_22's own `mov` slot 0 and 1, and `direct` slot 0/1, to
   confirm no local `PMVIE` in the target field itself.

## Why it matters

Confirms FSHIP_22/FSHIP_25 do not add new entries to the single-disc
movie relocation plan — their `MOVIE` opcode plays whatever stale
PMVIE-register value survives from earlier in the playthrough, not a
value either field or its caller sets. This matches the established
UNRESOLVED pattern (9 sites total) that the relocation plan already
treats as non-blocking, distinct from the 8 vanilla dead-code branches
(FSHIP_2/FSHIP_23-style) that were pruned as genuinely unreachable.

## Follow-ups

- [ ] Continue tracing remaining UNRESOLVED sites (if any still open) with
      this same live-caller-chain method before finalizing the movie
      relocation/dirent-reuse plan.
- [ ] Write the movie relocation and dirent-reuse plan doc (tracked
      separately in the task list).

## Sources

- `mods/single-disc/scripts/analyze_movie_reachability.py`
- `mods/single-disc/scripts/scan_csr_movie_reachability.py`
- `scripts/field_dat.py` (`split_script_at_return`, `fmt_op`)
- `docs/reference/field-id-mapping.txt`
