# FIELD.BIN extract and decompress (US disc 1)

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Tools:** CDImage B5 + `scripts/decompress_field_bin.py`

## Result

| Item | Value |
|------|-------|
| `FIELD.BIN` (GZIPPS) | 85435 bytes |
| `FIELD.BIN.dec` | 264008 bytes |
| GZIPPS sub-header | `dc 3d 03 00` |
| Encounter RNG table | file offset `0x40638` in `.dec` (`B1 CA EE 6C…`) |

Local backups: `ff7_disc1_pristine.bin`, `FIELD.BIN.pristine`.

## Notes

- Bulk extract of whole `FIELD` folder in CDImage hit “List index out of bounds”; single-file export of `FIELD.BIN` worked.
- Makou is not used for this extract (engine binary only).
