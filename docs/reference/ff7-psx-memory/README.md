# FF7 PSX memory map (imported)

Community **FF7 Memory Values** list, cleaned for this repo so agents and humans can search offsets quickly.

## Files

| File | Use |
|------|-----|
| `psx-address-list.json` | Full structured DB (preferred for tools) |
| `psx-address-list.jsonl` | One JSON object per line (grep-friendly) |
| `psx-address-list.csv` | Spreadsheet-friendly |
| `battle-related.md` | Filtered battle / end / input excerpt |
| `NOTES.md` | Import caveats (esp. controller vs mode bits) |
| `query_memory.py` | CLI search |

## Query

```bash
python3 docs/reference/ff7-psx-memory/query_memory.py victory
python3 docs/reference/ff7-psx-memory/query_memory.py 62D78
python3 docs/reference/ff7-psx-memory/query_memory.py 80062D78
python3 docs/reference/ff7-psx-memory/query_memory.py --tag battle-end
python3 docs/reference/ff7-psx-memory/query_memory.py --near 62D7C --span 0x40
```

Re-import after a new CSV drop:

```bash
python3 scripts/import_ff7_memory_values.py ~/Downloads/FF7\ Memory\ Values\ -\ PSX\ Address\ List.csv
```

## Address form

- Spreadsheet **PSX_Address** = offset in main RAM (e.g. `62D78`)
- `duckstation_va` = `0x80000000 + offset` when in main RAM range

## Source

`Copy of FF7 Memory Values.xlsx` / CSV export (Downloads).  
Primary sheet only: **PSX Address List**. PC sheets not in the DB.
