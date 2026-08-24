# Disc Transition Knowledge Base

**Last updated:** 2026-08-16
**Status:** Active investigation of single-disc D1→D2 transition issue

> **Note (verified 2026-08-24):** This doc references `scripts/build_field_db.py`,
> `scripts/query_field_scripts.py`, and `docs/reference/field-scripts.db`,
> none of which exist in this repo (see `docs/reference/field-scripts-database.md`).
> Those were a proposed tool, never built. The narrative findings below
> (field IDs, memory addresses, root-cause analysis, resolution in
> v0.1.3.1) are independently confirmed by `docs/findings/2026-08-20-slot-edit-origin.md`
> and `mods/single-disc/CHANGELOG.md` and remain accurate — only the
> "Investigation Tools" / query command sections describe a nonexistent tool.

## Quick Reference

| Topic | Resource |
|-------|----------|
| **Field scripts database** | `docs/reference/field-scripts.db` + query tools in `scripts/` |
| **PSX memory addresses** | `docs/reference/ff7-psx-memory/` (query_memory.py) |
| **Ghidra metadata** | `scripts/ghidra/*.json` (functions, symbols from all bins) |
| **Current INSTRUCTIONS** | `docs/INSTRUCTIONS.md` |
| **Recent findings** | `docs/findings/2026-08-*` |

## Key Memory Addresses

| Address | Size | Description | Var Name |
|---------|------|-------------|----------|
| `0x8009D588` | 256 bytes | Current disc number (1, 2, or 3) | Var[13] |
| `0x8011C2A4` | 2 bytes | Current field ID | - |
| `bank3[0x84]` bit 4 | 1 bit | Gate flag for LOST2→COS_BTM2 transition | - |

**Game Moment (GM):** 2-byte value at end of D1 = `0xa455`

## Key Field IDs

| Field ID | Name | Purpose |
|----------|------|---------|
| 103 | BLACKBGB | Disc swap hub (shows "insert disc 2" message) |
| 526 | COS_BTM2 | Cosmo Canyon break scene (bottom area) |
| 632 | LOSIN2 | End of Disc 1 (Jenova fight aftermath) |
| 634 | LOST2 | Forest near Cosmo Canyon (start of Disc 2) |

## Current Problem: Single-Disc D1→D2 Transition

### Reported Behavior

On **CSR + Single-disc**:
- ✅ Transition completes, loads field 634 (LOST2 forest)
- ❌ Missing break scene (should show COS_BTM2 field 526)
- ❌ No music on field 634

### Expected Behavior (CSR multi-disc)

**Needs confirmation via user playtest** (see INSTRUCTIONS.md):
1. End of D1: LOSIN2 → disc swap prompt
2. Swap to D2: loads → **break scene at COS_BTM2** (?)
3. After break: transition to LOST2 forest with music

### Analysis So Far

**2026-08-16 Finding:** Pristine BLACKBGB has **no MAPJUMP opcodes**
- Query: `python scripts/query_field_scripts.py --field BLACKBGB`
- Result: Only MUSIC opcodes present (in cloud/script31)
- Both D1 and D2 have identical BLACKBGB.DAT

**Implication:** The MAPJUMP #634 seen in single-disc is added by **CSR or single-disc mod**, not vanilla.

**From CHANGELOG analysis (v0.1.33-0.1.35):**
- Current single-disc uses **pure CSR D2** for LOST2 and COS_BTM2
- LOSIN2 (CSR D1) sets GM=0xa455 and **clears** bit4 in bank3[0x84]
- LOST2 on D2 checks bit4 → if clear, just RETurns (no break scene, no music)
- On multi-disc, disc initialization code sets bit4 → LOST2 forwards to COS_BTM2

**2026-08-20 Finding — root cause confirmed:** `docs/findings/2026-08-20-slot-edit-origin.md`
(section "LOST2 (field #634), init:0") decoded the raw script for the
`init:0` slot of LOST2 (field #634) on both discs. CSR D2's version of
this slot contains the missing `MAPJUMP field #526 (COS_BTM2)` block
(gated by the GM 0xa455 check), which CSR D1's version completely lacks
— D1 only adds a duplicate-music guard, no transition logic. If the
current single-disc merge is taking CSR D1's `init:0` for LOST2 instead
of CSR D2's, that alone explains both the missing break scene and the
missing music on field 634. Verdict: take CSR D2 for this slot.

**2026-08-20 (later) — v0.1.3 shipped this fix but the *layer* corrupted
it in transit:** `build_work_bin.py` correctly wrote CSR D2's LOST2 (and
the other 8 rework fields) into the merged work bin, but the publish step
diffed that work bin against **pristine** Disc 1 instead of the **CSR
v0.14.1 base** the builder stacks the layer on top of. Any byte where the
merge coincidentally matched pristine — while CSR's base layer had
already changed that byte — produced no diff record, so the stale CSR
byte silently survived under the layer instead of being overwritten. This
made `BLACKBGB`, `LOST2`, and `NIVGATE` fail to parse entirely (explains
both the missing D1→D2 save prompt — BLACKBGB is the disc-swap hub — and
field 634 failing to load), and left `BUGIN1A`/`RCKTIN2`/`RCKTIN7` with a
handful of wrong bytes. Fixed in v0.1.3.1 by re-diffing the same work bin
against the CSR base; see `mods/single-disc/CHANGELOG.md` 0.1.3.1 entry
and `tests/test_single_disc_stack.py::test_rework_fields_parse_and_match_csr_source`.

## Investigation Tools

### Field Scripts Database

```bash
# Build/update database
python scripts/build_field_db.py

# Query specific field
python scripts/query_field_scripts.py --field BLACKBGB

# Find all MAPJUMP opcodes
python scripts/query_field_scripts.py --opcode MAPJUMP

# List fields in database
python scripts/query_field_scripts.py --list
```

### PSX Memory Map

```bash
# Search for disc-related addresses
python docs/reference/ff7-psx-memory/query_memory.py disc

# Search for field-related addresses
python docs/reference/ff7-psx-memory/query_memory.py field
```

### Ghidra Metadata

```python
import json
from pathlib import Path

# Check FIELD.BIN functions
field_funcs = json.loads(Path("scripts/ghidra/field-functions.json").read_text())
disc_funcs = [f for f in field_funcs if 'disc' in f.get('name', '').lower()]
```

## Next Steps

1. **User playtest CSR multi-disc** (see INSTRUCTIONS.md)
   - Confirm actual disc 1→2 flow
   - Identify where break scene happens
   - Record field IDs and music behavior

2. **Analyze CSR BLACKBGB** (after playtest confirmation)
   - Extract from CSR D1 and D2 discs
   - Add to field-scripts.db: `--sources csr`
   - Query to see what CSR adds to BLACKBGB

3. **Design fix** (based on CSR behavior)
   - Option A: Make BLACKBGB MAPJUMP #526 (break) then #634 (forest)
   - Option B: Set bit4 before MAPJUMP #634 (like v0.1.29 tried)
   - Option C: Patch LOST2 to always forward to COS_BTM2
   - Option D: Something else based on CSR analysis

## Query Examples

### Compare BLACKBGB across sources

```python
import sqlite3
conn = sqlite3.connect("docs/reference/field-scripts.db")

# Count opcodes per source
conn.execute('''
    SELECT f.source, o.opcode_name, COUNT(*) 
    FROM fields f
    JOIN opcodes o ON f.id = o.field_id
    WHERE f.field_name = 'BLACKBGB' AND f.disc = 1
    GROUP BY f.source, o.opcode_name
''').fetchall()
```

### Find MAPJUMP targets in disc transition fields

```sql
SELECT f.field_name, f.disc, f.source, o.entity, o.param_text
FROM fields f
JOIN opcodes o ON f.id = o.field_id
WHERE f.field_name IN ('LOSIN2', 'LOST2', 'BLACKBGB', 'COS_BTM2')
  AND o.opcode_name = 'MAPJUMP'
ORDER BY f.field_name, f.disc, f.source;
```

## References

- **Makou Reactor source:** `workspace/makoureactor/src/core/field/`
- **Opcode definitions:** `workspace/makoureactor/src/core/field/Opcode.h`
- **Field DAT parser:** `scripts/field_dat.py`
- **ISO utilities:** `scripts/psx_mode2_iso.py`
