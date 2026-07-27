# WORLD.BIN extract + decompress OK

**Date:** 2026-07-28  
**Confidence:** confirmed  
**Related:** [world-map-encounter-plan](2026-07-27-world-map-encounter-plan.md)

## Evidence

| | Size |
|--|------|
| `WORLD.BIN` (GZIPPS) | 66715 |
| `WORLD.BIN.dec` | 164032 |

Header `xxd`: `c0 80 02 00` = LE dec size `0x000280C0` = 164032; then `54 e4 04 00`; gzip magic `1f 8b` at offset 8.

Decompress via `scripts/decompress_gzipps.py` (no Field RNG table — expected).

## Next

Align Ghidra import base with DuckStation (search RAM for start of `.dec` while on world map).
