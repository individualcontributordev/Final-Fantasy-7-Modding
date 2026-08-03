# No-swap — FIELD DSKCG + MOVIE engine stubs

**Date:** 2026-08-03
**Confidence:** likely (static RE; playtest required)
**Overlay:** FIELD/FIELD.BIN GZIPPS at VA 0x800A0000

## Handlers (NTSC-U)

Opcode table file 0x40228 (VA 0x800E0228).

| Op | Name | Handler VA | FILE off | Stub |
|----|------|------------|----------|------|
| 0x0E | DSKCG (Ask disc) | 0x800C523C | 0x2523C | jr ra; nop |
| 0xF9 | MOVIE (Play movie) | 0x800CCE94 | 0x2CE94 | jr ra; nop |

PMVIE 0xF8 left alone (set id only).

Battle Supernova / SNOVA is separate (not FIELD MOVIE).

## Tool

mods/no-swap/scripts/stub_field_movie_dskcg.py

## Policy

clean/Highwind: always stub both. CSR: always DSKCG; MOVIE whitelist later.
