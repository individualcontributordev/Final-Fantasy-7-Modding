# Field Scripts Database

**Location:** `docs/reference/field-scripts.db`  
**Purpose:** SQLite database for fast querying of FF7 field script opcodes across different disc images

## Schema

### `fields` table

Stores metadata about each analyzed field:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `field_name` | TEXT | Field name (e.g., "BLACKBGB") |
| `disc` | INTEGER | Disc number (1, 2, or 3) |
| `source` | TEXT | Source image ("pristine", "csr-d1", "csr-d2", "single-disc") |
| `num_scripts` | INTEGER | Total script slots in the field |
| `file_size` | INTEGER | Compressed .DAT file size in bytes |

**Unique constraint:** (field_name, disc, source)

### `opcodes` table

Stores individual opcodes from each field script:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `field_id` | INTEGER | Foreign key to `fields.id` |
| `entity` | TEXT | Entity name (e.g., "cloud", "init") |
| `script_slot` | INTEGER | Script slot number (0-31) |
| `offset` | INTEGER | Byte offset in script |
| `opcode` | INTEGER | Opcode byte value (e.g., 0x2B for MAPJUMP) |
| `opcode_name` | TEXT | Human-readable name ("MAPJUMP", "MUSIC", etc.) |
| `param1` | INTEGER | First parameter (if applicable) |
| `param2` | INTEGER | Second parameter (if applicable) |
| `param_text` | TEXT | Human-readable parameter description |

**Indexed on:** field_id, opcode_name, opcode

## Tracked Opcodes

Currently stores these opcodes (can be extended):

| Opcode | Name | Purpose | Params |
|--------|------|---------|--------|
| 0x00 | RET | Return from script | None |
| 0x2B | MAPJUMP | Jump to another field | param1=field_id |
| 0x2C | SETBYTE | Set memory byte | param1=bank, param2=value |
| 0x31 | MUSIC | Play music track | param1=music_id |
| 0x33 | IFUW | If unsigned word | param1=var, param2=else_offset |
| 0x34 | IFSW | If signed word | param1=var, param2=else_offset |
| 0x35 | IFUB | If unsigned byte | param1=var, param2=else_offset |
| 0x36 | IFUBL | If unsigned byte (long) | param1=var, param2=else_offset |

## Building the Database

```bash
# Build with default fields (transition-related)
python scripts/build_field_db.py

# Build specific fields
python scripts/build_field_db.py --fields BLACKBGB LOST2 COS_BTM2

# Build from specific sources
python scripts/build_field_db.py --sources pristine csr
```

## Querying

### Command-line tool

```bash
# Show all opcodes in a field
python scripts/query_field_scripts.py --field BLACKBGB

# Filter by disc and source
python scripts/query_field_scripts.py --field LOST2 --disc 2 --source pristine

# Find all instances of an opcode
python scripts/query_field_scripts.py --opcode MAPJUMP

# List all fields in database
python scripts/query_field_scripts.py --list
```

### Direct SQL queries

```python
import sqlite3
conn = sqlite3.connect("docs/reference/field-scripts.db")
cursor = conn.cursor()

# Find all MAPJUMP targets in LOST2
cursor.execute('''
    SELECT f.disc, f.source, o.entity, o.script_slot, o.param_text
    FROM fields f
    JOIN opcodes o ON f.id = o.field_id
    WHERE f.field_name = 'LOST2' AND o.opcode_name = 'MAPJUMP'
''')

# Compare BLACKBGB across discs
cursor.execute('''
    SELECT f.disc, f.source, COUNT(*) as count
    FROM fields f
    JOIN opcodes o ON f.id = o.field_id
    WHERE f.field_name = 'BLACKBGB' AND o.opcode_name = 'MAPJUMP'
    GROUP BY f.disc, f.source
''')
```

## Common Analysis Queries

### Find fields with disc transition logic

```sql
SELECT DISTINCT f.field_name, f.disc, f.source
FROM fields f
JOIN opcodes o ON f.id = o.field_id
WHERE o.opcode_name = 'MAPJUMP' AND o.param1 IN (526, 634)
ORDER BY f.field_name;
```

### Compare a field across sources

```sql
SELECT f.source, o.opcode_name, COUNT(*) as count
FROM fields f
JOIN opcodes o ON f.id = o.field_id
WHERE f.field_name = 'BLACKBGB' AND f.disc = 1
GROUP BY f.source, o.opcode_name
ORDER BY f.source, o.opcode_name;
```

### Find all music changes in a field

```sql
SELECT f.disc, f.source, o.entity, o.script_slot, o.offset, o.param_text
FROM fields f
JOIN opcodes o ON f.id = o.field_id
WHERE f.field_name = 'BLACKBGB' AND o.opcode_name = 'MUSIC'
ORDER BY f.disc, f.source, o.offset;
```

## Use Cases

1. **Compare pristine vs. CSR vs. single-disc** - quickly see what changed
2. **Find missing opcodes** - identify where CSR or single-disc removed disc checks
3. **Track transition paths** - follow MAPJUMP chains across fields
4. **Debug music issues** - see where MUSIC opcodes are placed
5. **Analyze script flow** - trace IF/ELSE branches and RET points

## Extending

To track additional opcodes, edit `scripts/build_field_db.py`:

1. Add opcode to `OPCODE_NAMES` dict
2. Add parsing logic in `analyze_field()` if parameters needed
3. Rebuild database with `python scripts/build_field_db.py`
