# No-swap (full-run) — WIP

Single-disc / no disc-swap pack. **Not shipped** until full-run playtest.

## Policy

| Base (later packs) | Ask disc (DSKCG) | Field FMV (MOVIE) | Supernova |
|--------------------|------------------|-------------------|-----------|
| clean | stub skip | stub skip all | TODO battle stub |
| CSR | stub skip | stub skip except manip whitelist | TODO |
| Highwind | stub skip | stub skip all | TODO |

Engine stubs preferred over editing every field script.

## FIELD.BIN stubs (found)

Load VA base `0x800A0000`. Opcode table file `0x40228`.

| Op | Name | Handler VA | FILE off | Stub |
|----|------|------------|----------|------|
| 0x0E | DSKCG | 0x800C523C | 0x2523C | jr ra; nop |
| 0xF9 | MOVIE | 0x800CCE94 | 0x2CE94 | jr ra; nop |

Tool: `scripts/stub_field_movie_dskcg.py`
