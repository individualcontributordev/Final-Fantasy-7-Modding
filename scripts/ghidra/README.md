# Ghidra Metadata for FF7 PSX Binaries

**Purpose:** Complete function and symbol metadata extracted from all 5 core FF7 PSX executables

## Files

### Function Metadata (JSON)

| File | Module | Functions | Description |
|------|--------|-----------|-------------|
| `field-functions.json` | FIELD.BIN | 186 | Field engine, encounters, scripts |
| `battle-functions.json` | BATTLE.X | 615 | Battle engine, attacks, AI |
| `batres-functions.json` | BATRES.X | 18 | Victory fanfare, rewards |
| `world-functions.json` | WORLD.BIN | 446 | World map engine, movement |
| `scus-941-63-functions.json` | SCUS_941.63 | 1,145 | Main kernel, module loader, CD APIs |

**Total:** 2,410 functions with addresses, sizes, and call graphs

### Symbol Metadata (JSON)

Corresponding `*-symbols.json` files contain named symbols (if any) for each module.

## Function JSON Format

```json
{
  "name": "FUN_800c5cd4",
  "address": "800c5cd4",
  "size": 1072,
  "callers": ["800b5e28"]
}
```

- `name`: Function name (auto-generated `FUN_*` if no symbol)
- `address`: PSX RAM address (hex string without `0x` prefix)
- `size`: Function size in bytes
- `callers`: Array of addresses that call this function

## Usage Examples

### Find disc-related functions

```python
import json
from pathlib import Path

world_funcs = json.loads(Path("scripts/ghidra/world-functions.json").read_text())
disc_funcs = [f for f in world_funcs if 'disc' in f.get('name', '').lower() or 'cd' in f.get('name', '').lower()]

for f in disc_funcs:
    print(f"{f['address']}: {f['name']} ({f['size']} bytes, {len(f.get('callers', []))} callers)")
```

### Find largest functions (potential candidates for complex logic)

```python
sorted_funcs = sorted(world_funcs, key=lambda x: x.get('size', 0), reverse=True)[:10]
for f in sorted_funcs:
    print(f"{f['address']}: {f['name']} ({f['size']} bytes)")
```

### Find a specific function by address

```python
target = [f for f in world_funcs if f.get('address') == '800c5cd4']
if target:
    print(json.dumps(target[0], indent=2))
```

## Key Findings (from 2026-08-15 analysis)

### FIELD.BIN
- **FUN_800cdc14** @ `0x800cdc14` (20 bytes, 0 callers)
  - Only disc-related function found
  - Likely unused or data reference
  - **No action needed** - DSKCG opcodes already stripped via Makou Reactor

### WORLD.BIN
- **FUN_800c5cd4** @ `0x800c5cd4` (1072 bytes, 1 caller: `800b5e28`)
  - Large function with potential disc/CD logic
  - **Needs investigation:** Could be world map disc check or CD streaming
  - See `docs/findings/2026-08-15-ghidra-metadata-single-disc-analysis.md`

### BATTLE.X
- **11 functions** with "cd" in name (CD-ROM utilities, not disc checks)
- **FUN_800d4d90** contains all 17 SNOVA LBA references (already patched)
- **No new action needed**

### BATRES.X
- **0 disc-related functions**
- Victory fanfare has no disc checks
- **No action needed**

### SCUS_941.63
- **42 functions** (all Sony CD-ROM BIOS APIs)
- System-level CD APIs like `CdInit`, `CdRead2`, `CdControl`
- These are kernel services used by all modules
- **No action needed**

## Cross-Reference with PSX Memory Map

The PSX memory addresses from Ghidra can be cross-referenced with:
- `docs/reference/ff7-psx-memory/psx-address-list.json` - DuckStation memory map
- `docs/reference/ff7-psx-memory/query_memory.py` - CLI query tool

Example:
```bash
# Find disc-related memory addresses
python docs/reference/ff7-psx-memory/query_memory.py disc

# Output: 0x8009D588 - Current Disc (Var[13])
```

## Extraction Scripts

- `extract_all_bins.py` - Extracts metadata from all 5 binaries
- `extract_field_metadata.py` - Specialized FIELD.BIN extraction
- `ExtractFieldMetadata.java` - Ghidra headless script

## References

- **Ghidra project:** Binary analysis of FF7 PSX executables
- **PSX memory map:** Cross-reference with runtime addresses
- **Field scripts DB:** Complement binary analysis with field script opcodes
- **Single-disc analysis:** `docs/findings/2026-08-15-ghidra-metadata-single-disc-analysis.md`

## Conclusion

The Ghidra metadata **confirms** no missed disc checks in:
- ✅ FIELD.BIN (already stripped via Makou)
- ✅ BATTLE.X (already patched SNOVA LBAs)
- ✅ BATRES.X (no disc code)
- ✅ SCUS (only CD BIOS APIs, not disc-ID checks)

**Only potential issue:** WORLD.BIN function `FUN_800c5cd4` - needs disassembly to verify it doesn't check disc IDs for world map events.
