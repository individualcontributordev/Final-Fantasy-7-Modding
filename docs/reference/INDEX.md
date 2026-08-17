# FF7 PSX Reference Data Index

Complete reference data for FF7 PSX modding. All data extracted from [Makou Reactor 2.1.0](https://github.com/myst6re/makoureactor).

## Quick Reference

| Type | Count | File | Query Tool |
|------|-------|------|------------|
| **Fields** | 788 | `field-id-mapping.txt` | `python3 scripts/query_ff7_ids.py field <id-or-name>` |
| **Movies** | 106 | `movie-id-mapping.txt` | `python3 scripts/query_ff7_ids.py movie <id>` |
| **Music** | 100 | `music-id-mapping.txt` | `python3 scripts/query_ff7_ids.py music <id>` |
| **Memory** | ~300 regions | `ff7-psx-memory/*.txt` | `python3 docs/reference/ff7-psx-memory/query_memory.py <addr-or-keyword>` |

## Usage Examples

```bash
# Field lookup (by ID or name, supports fuzzy search)
python3 scripts/query_ff7_ids.py field 637        # → loslake1
python3 scripts/query_ff7_ids.py field loslake1   # → ID 637
python3 scripts/query_ff7_ids.py field lost       # → fuzzy: lost1, lost2, lost3, loslake*

# Movie lookup (hex or decimal)
python3 scripts/query_ff7_ids.py movie 0x2f       # → jairofal (Disc1)
python3 scripts/query_ff7_ids.py movie 47         # → same

# Music lookup
python3 scripts/query_ff7_ids.py music 82         # → lb2 "One-Winged Angel"

# Memory lookup (RAM address or symbol)
python3 docs/reference/ff7-psx-memory/query_memory.py 0x800C4E14  # → Battle encounter table
python3 docs/reference/ff7-psx-memory/query_memory.py materia     # → All materia-related addresses
```

## File Formats

### field-id-mapping.txt
```
# Format: ID NAME
0 test0
1 junair
...
637 loslake1
...
787 frcyo2
```

### movie-id-mapping.txt
```
# Format: ID FILENAME DISC
0 fship2 Common        # Movies 0-19: All discs
20 mkup Disc1          # Movies 20-53: Disc 1 only
54 greatpit Disc2      # Movies 54-95: Disc 2 only
96 last4_2 Disc3       # Movies 96-105: Disc 3 only
```

**PMVIE Opcode:** `f8 XX` (XX = hex movie ID)
- Example: `f82f` = movie 0x2F (47) = jairofal

### music-id-mapping.txt
```
# Format: ID INTERNAL_NAME "FULL_TITLE"
0 none "none"
2 oa "Opening - Bombing Mission"
82 lb2 "One-Winged Angel"
99 roll "Staff Roll"
```

**MUSIC Opcode:** `f0 XX` (XX = hex music ID)
- Example: `f052` = music 0x52 (82) = One-Winged Angel

## Python API

All reference files are plain text — no database required.

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # From docs/reference/

# Load field mapping
fields = {}
for line in (ROOT / "docs/reference/field-id-mapping.txt").read_text().splitlines():
    if line and not line.startswith('#'):
        field_id, name = line.split(maxsplit=1)
        fields[int(field_id)] = name

# Load movie mapping
movies = {}
for line in (ROOT / "docs/reference/movie-id-mapping.txt").read_text().splitlines():
    if line and not line.startswith('#'):
        parts = line.split()
        if len(parts) >= 3:
            movies[int(parts[0])] = (parts[1], parts[2])  # (filename, disc)

# Load music mapping
music = {}
for line in (ROOT / "docs/reference/music-id-mapping.txt").read_text().splitlines():
    if line and not line.startswith('#'):
        parts = line.split(maxsplit=2)
        if len(parts) >= 3:
            music[int(parts[0])] = (parts[1], parts[2].strip('"'))  # (internal, title)

# Example usage
field_name = fields[637]  # "loslake1"
movie_file, disc = movies[47]  # ("jairofal", "Disc1")
track_internal, track_title = music[82]  # ("lb2", "One-Winged Angel")
```

## Key Mappings for Single-Disc Modding

### Critical Fields
| ID | Name | Purpose |
|----|------|---------|
| 103 | blackbgb | Hub with disc swap prompts (DSKCG removals) |
| 104 | blackbge | Ending hub (DSKCG removals) |
| 105 | blackbg3 | Hub variant (DSKCG removals) |
| 526 | cos_btm2 | Cosmo Canyon break scene (disc 2 entry point) |
| 634 | lost2 | Disc 1→2 transition (IFUW patch required) |
| 637 | loslake1 | Contains movie 0x2F (jairofal) — flicker issue |

### Critical Movies
| ID | File | Disc | Issue |
|----|------|------|-------|
| 47 | jairofal | Disc1 | Audio flicker in loslake1 (field 637) |
| 101 | ending1 | Disc3 | Audio flicker in ending |
| 102 | ending3 | Disc3 | Ending movie |
| 105 | ending2 | Disc3 | Audio flicker in ending |

## Source

- **Makou Reactor:** https://github.com/myst6re/makoureactor
- **Source File:** `src/Data.cpp` (lines 607-849)
- **Extracted:** 2026-08-17
- **Version:** Makou Reactor 2.1.0

## Related Tools

| Tool | Purpose |
|------|---------|
| `scripts/query_ff7_ids.py` | Query field/movie/music IDs |
| `scripts/field_dat.py` | Parse field DAT structure |
| `scripts/decode_field_script.py` | Decode field script opcodes |
| `scripts/compare_field_dat.py` | Compare field files between bins |
| `docs/reference/ff7-psx-memory/query_memory.py` | Query PSX RAM addresses |

## Maintenance

**When to update:**
- Never (static reference from Makou Reactor 2.1.0)
- These are the canonical PSX field/movie/music IDs
- Future mods may reference additional files, but IDs are fixed

**When new data is needed:**
- Add new reference files in this directory
- Update this INDEX.md
- Add query support to `scripts/query_ff7_ids.py` if applicable
