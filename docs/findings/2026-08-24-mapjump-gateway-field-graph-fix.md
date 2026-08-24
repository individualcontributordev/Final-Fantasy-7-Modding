# Field-level reachability: MAPJUMP+gateway graph corrects earlier "58 reachable" scan

**Date:** 2026-08-24
**Confidence:** confirmed
**Status:** open
**Related:** docs/findings/2026-08-24-csr-movie-reachability-scan.md (superseded numbers below)

## Summary

The earlier same-day scan (58/57/58 movies "reachable" per disc) only did
**intra-script** CFG reachability — it assumed every `FIELD/*.DAT` is itself
entered by the player and treated `MAPJUMP` (0x60) as a harmless fallthrough
opcode. Both assumptions are wrong:

1. **`MAPJUMP` is terminal, not fallthrough.** It's a 10-byte "Change Field"
   opcode (ffrtt: field id + X/Y/Z + direction) that hands control to a
   *different* field's script entirely. Anything physically after it in the
   same slot is dead code unless something else jumps back in. Confirmed via
   ffrtt wiki (`FF7/Field/Script/Opcodes/60_MAPJUMP`) and prevalence-checked:
   1,863 hits in the first 2,000 field scripts scanned.
2. **No field-level graph existed.** A field's PMVIE could show "reachable"
   internally even if CSR/the engine never lets the player enter that field
   at all. Fields are entered two ways:
   - Scripted `MAPJUMP`, now BFS-walked as a terminal-edge field-to-field
     graph.
   - **Walkmesh gateways** (doors/exit lines) — a field-file section (index 4
     in `FieldDat.sections`, ffrtt calls it "Triggers") with a 12-entry,
     24-byte gateway table at offset 56. Each entry's bytes `[18:2]` are the
     destination field id (u16 LE); unused slots are `0x7FFF`. These are
     **not** script opcodes at all — a pure CFG/opcode scan can never see
     them. Verified against MD1STIN (the entry field): gateway 0 → field id
     117 (`md1_1`), matching `docs/reference/field-id-mapping.txt`.

## Fix

- `analyze_movie_reachability.py`:
  - Added `MAPJUMP` to a new `MAPJUMP_TERMINAL` set, checked alongside
    `TERMINALS` in `edges()` — no fallthrough edge past a reachable MAPJUMP.
  - `SlotAnalysis.reachable_mapjump_targets()` — field ids from MAPJUMP ops
    that survived the intra-script BFS.
  - `field_gateway_targets()` — parses section 5's gateway table directly
    (offset 56, 12 * 24 bytes, field id at `+18`, skip `0x7FFF` placeholders).
    Gateways are always "live" (no scripted skip mechanism applies to them),
    so we don't attempt walkmesh-polygon-level reachability inside a field —
    just "does this field have *a* gateway to field X".
- `scan_csr_movie_reachability.py`:
  - `ENTRY_FIELD_ID = 116` (`md1stin` — Reactor 1 train platform, the first
    field a new-game playthrough enters; confirmed via
    `field-id-mapping.txt` + ff7speedruns.com "md1stin is the first field
    map in Reactor 1").
  - `build_field_graph()` — field NAME -> set of destination field ids, from
    reachable MAPJUMP + all gateways.
  - `reachable_field_names()` — BFS from `ENTRY_FIELD_ID` over that graph,
    id->name via `docs/reference/field-id-mapping.txt`, restricted to field
    names actually present on this disc.
  - `scan_disc()` now ANDs intra-script PMVIE reachability with field-level
    reachability: a movie only counts reachable if its field is entered
    AND its PMVIE survives the intra-script BFS.

## Corrected results (CSR D1/D2/D3, pristine + CSR layer only, no single-disc)

| Disc | Fields on disc | Fields reachable from entry | Movies reachable | Movies dead |
|------|----------------|------------------------------|-------------------|-------------|
| D1 | 787 (82 placeholder) | 377 | **24** | 36 |
| D2 | 787 (82 placeholder) | 361 | **27** | 33 |
| D3 | 787 (82 placeholder) | 333 | **23** | 37 |

This matches the user's premise: **most movies on each disc are in fact
skipped/unreachable in CSR** — the field-level graph was the missing piece,
not just intra-script jump analysis. The earlier "58 reachable" figure was
inflated by counting every field as entered.

### D1 reachable (24)
BIKEGET.MOV, BRGNVL.MOV, CAR_1209.STR, FALLPL.MOV, GOLD1.MOV, JUNAIRD.STR,
JUNAIRU.STR, JUNELEGO.STR, JUNELEIN.STR, JUNIN_GO.STR, JUNIN_IN.STR,
MAINPLR.MOV, MK8.STR, MKUP.STR, MTNVL.STR, MTNVL2.STR, NIVLSFS.MOV,
NORTHMK.MOV, NVLMK.MOV, ONTRAIN.MOV, OOB(54), PLREXP.MOV, SMK.STR,
SOUTHMK.MOV

### D2 reachable (27)
CANON.MOV, CANONH1P.MOV, CANONH3F.MOV, CANONHT1.MOV, CANONHT2.MOV,
CANONON.MOV, C_SCENE1.MOV, C_SCENE2.MOV, C_SCENE3.MOV, FF_DAIKU.MOV,
GELNICA.MOV, GREATPIT.MOV, HWINDFLY.MOV, HWINDJET.MOV, JUNAIRD.STR,
JUNAIRU.STR, JUNELEGO.STR, JUNELEIN.STR, JUNIN_GO.STR, JUNIN_IN.STR,
METEOSKY.MOV, NRCRL.MOV, NRCRLB.MOV, PHOENIX.MOV, WEAPON0.MOV, WEAPON1.MOV,
WEAPON4.MOV

### D3 reachable (23)
ENDING01.MOV, ENDING3E.MOV, FCAR.STR, JUNAIRD.STR, JUNAIRU.STR,
JUNELEGO.STR, JUNELEIN.STR, JUNIN_GO.STR, JUNIN_IN.STR, LAST4_2.BIN,
LAST4_3.BIN, LAST4_4.MOV, LASTFLOR.MOV, LASTMAP.BIN, OOB(30..35, 40, 52, 54)

Raw JSON: `/tmp/csr_movie_reachability_v3.json` (not committed — regenerate
via `python3 mods/single-disc/scripts/scan_csr_movie_reachability.py -o ...`).

## Caveats / not yet done

- Gateway reachability is field-level only ("does field X have a gateway to
  field Y"), not walkmesh-polygon-connectivity-level ("can the player's
  sector actually reach that gateway's line"). If CSR blocks a polygon
  sector rather than removing/rerouting a gateway, this scan would still
  count that gateway's destination as reachable. No known CSR case uses
  this trick, but it's unverified.
- `PMJMP`/`PMJMP2` (0xD8/0xD9, "Prepare Field Change") aren't graph edges
  yet — they only *stage* an ID for a subsequent MAPJUMP-like transition and
  don't carry XYZD, so they don't independently define a target the same
  way. Not observed gating any PMVIE-reachable field in this scan; flag for
  follow-up if a field's only path in is via PMJMP-adjacent logic.
- World-map fields (ids 1-100, `wm*`) are unions of the walkable field graph
  via LSTMP/world-map field switch too; not separately validated here since
  no PMVIE-bearing field flagged as unreachable was gated purely by wm*
  transitions in this pass.
- This scan is plain CSR D1/D2/D3 (pristine + CSR layer), **not** the
  single-disc build. Single-disc adds further field trims/movie-slot
  overwrites on top (see `mods/single-disc/patches/field-movie-trims.md`,
  `csr-manip-movie-seed.txt`) that aren't reflected here — those change
  disc-specific field bytes but don't change field IDs/gateways, so the
  entry-field graph itself should carry over; PMVIE-level results would
  need a rerun against the built single-disc bin if needed.

## Sources

- `mods/single-disc/scripts/analyze_movie_reachability.py`
- `mods/single-disc/scripts/scan_csr_movie_reachability.py`
- ffrtt wiki: `FF7/Field/Script/Opcodes/60_MAPJUMP`, `FF7/Field/Triggers`,
  `FF7/Field/Field_ID`
- `docs/reference/field-id-mapping.txt`
