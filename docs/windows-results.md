# Windows → Mac results

**Status:** complete
**Task:** extract and decompress FIELD.BIN

## Output

FIELD.BIN size (bytes): 85435
FIELD.BIN.dec size (bytes): 264008
RNG table line (full script line): RNG table found at file offset 0x40638
Errors (or none): none

## Notes

- Disc images renamed to `ff7_disc1.bin` / `.cue` (and disc 2–3) before extract
- `ff7_disc1_pristine.bin` backup exists
- `FIELD.BIN.pristine` backup exists
- Extracted via CDImage B5 (single-file export; bulk FIELD folder export hit "List index out of bounds")
- GZIPPS sub-header: `dc3d0300`
- Expected dec size from header: 264008 bytes (matches output)
