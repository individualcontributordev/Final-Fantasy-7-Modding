# Align Ghidra import base with DuckStation (FIELD.BIN @ 0x800A0000)

**Date:** 2026-07-25  
**Confidence:** likely (pending DuckStation byte check)

## Target

| Item | Address |
|------|---------|
| FIELD.BIN load / Ghidra base | `0x800A0000` |
| `increment_step_id` | `0x800AB9C8` |
| RNG table | `0x800E0638` |
| StepID (BSS, unchanged) | `0x8009C540` |
| Offset | `0x8009AD2C` |

Signature at `increment_step_id`: `0A 80 02 3C` (`lui v0,0x800a`) then `40 C5 42 90` (`lbu v0,-0x3ac0(v0)`).  
Signature at table: `B1 CA EE 6C 5A 71 2E 55`.
