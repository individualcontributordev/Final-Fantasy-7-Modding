# FF7 Reference Data

Complete reference mappings for FF7 PSX field, movie, and music IDs extracted from [Makou Reactor](https://github.com/myst6re/makoureactor).

## Files

| File | Contents | Count |
|------|----------|-------|
| `field-id-mapping.txt` | Field ID → Field Name | 788 fields |
| `movie-id-mapping.txt` | Movie ID → Filename + Disc | 106 movies |
| `music-id-mapping.txt` | Music ID → Track Name | 100 tracks |

## Quick Lookup

Use the query utility:

```bash
# Field lookup (by ID or name)
python3 scripts/query_ff7_ids.py field 637
python3 scripts/query_ff7_ids.py field loslake1
python3 scripts/query_ff7_ids.py field lost  # fuzzy search

# Movie lookup (decimal or hex)
python3 scripts/query_ff7_ids.py movie 47
python3 scripts/query_ff7_ids.py movie 0x2f

# Music lookup
python3 scripts/query_ff7_ids.py music 82
```

## Field IDs

**Format:** `ID NAME`

**Examples:**
- `103 blackbgb` - Hub area with disc swap prompts
- `526 cos_btm2` - Cosmo Canyon break scene (disc 2 start)
- `634 lost2` - Lost Forest (disc 2 transition)
- `637 loslake1` - Lost Number lake area

**Range:** 0-787 (788 total)

## Movie IDs

**Format:** `ID FILENAME DISC`

**Disc Distribution:**
- **0-19:** Common (all discs)
- **20-53:** Disc 1 exclusive
- **54-95:** Disc 2 exclusive
- **96-105:** Disc 3 exclusive

**Examples:**
- `47 jairofal Disc1` - Movie 0x2F in LOSLAKE1 (flicker issue)
- `101 ending1 Disc3` - Ending movie (flicker issue)
- `91 loslake1 Disc2` - LOSLAKE1 related movie

**PMVIE Opcode:** `f8 XX` where XX is hex movie ID
- Example: `f82f` = movie 0x2F (47) = jairofal

## Music IDs

**Format:** `ID INTERNAL_NAME "FULL_TITLE"`

**Examples:**
- `2 oa "Opening - Bombing Mission"`
- `82 lb2 "One-Winged Angel"`
- `99 roll "Staff Roll"`

**MUSIC Opcode:** `f0 XX` where XX is hex music ID
- Example: `f052` = music 0x52 (82) = One-Winged Angel

## Source

All data extracted from Makou Reactor 2.1.0:
- Repository: https://github.com/myst6re/makoureactor
- File: `src/Data.cpp` (lines 607-849)
- Arrays: `movieList[106]`, `_mapList[788]`, `musicList[100]`, `musicList2[100]`

## Usage in Scripts

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Load field mapping
fields = {}
for line in (ROOT / "docs/reference/field-id-mapping.txt").read_text().splitlines():
    if line and not line.startswith('#'):
        field_id, name = line.split(maxsplit=1)
        fields[int(field_id)] = name

# Example: Get field name
field_name = fields[637]  # "loslake1"
```

## Related Tools

- **Makou Reactor:** GUI editor for field files
- **`scripts/field_dat.py`:** Python parser for field structure
- **`scripts/decode_field_script.py`:** Opcode decoder
- **`scripts/query_ff7_ids.py`:** This query utility

## Movie Flicker Investigation

**Current Issues (v0.1.2):**
- Movie 0x2F (47) "jairofal" in LOSLAKE1 - audio flicker
- Ending movies (101, 102, 105) - audio flicker

**Hypothesis:** 
Single-disc builds move Disc 2/3 movies to Disc 1, but movie pointers or data may be incomplete/corrupted.

See: `docs/findings/2026-08-17-movie-flicker-investigation.md`
