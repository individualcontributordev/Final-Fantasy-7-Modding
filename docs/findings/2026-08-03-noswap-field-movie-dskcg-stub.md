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

## Playtest v1 failure (2026-08-03)

Bare jr ra; nop at handler entry caused **new game black screen**.
Field opcode handlers must advance the entity script PC or the same op re-executes forever.

## v2 stub

Same DSKCG/MOVIE offsets, 16 instructions:

- index = *(u8*)0x800722C4
- pc = *(u16*)(0x800831FC + index*2)
- *pc += 1 (MOVIE) or += 2 (DSKCG)
- return 0

Tool updated accordingly.

## Playtest v2 (2026-08-03)

PC-advance-only stub: operator heard movie audio on black screen; field never
loaded after audio ended. MOVIE handler is multi-state — first entries set
entity status / flags and wait; completion path clears status@+1, half@+38,
advances PC, returns 0. Must replicate completion, not only PC++.

## v3

Full completion stub at MOVIE/DSKCG entry (see tool).

## v3 playtest FAIL

Still audio + black + no field load. Entity pointer writes at intro are suspect.

## v4

No entity dereference. Fast-path style: PC+=delta, clear 0x80071C1C + 0x801144D4, v0=0, jr ra.

## v4 FAIL + pivot (2026-08-03)

v4 same softlock (audio ~1:30 intro, no field). Replacing MOVIE entry is abandoned
for playable builds.

## v5

Default tool patches **DSKCG only**. MOVIE vanilla. Full FMV-skip needs another
layer (e.g. stream player), not opcode 0xF9 entry rewrite.

## v5 playtest (2026-08-03)

- Intro + first field: **PASS** (MOVIE vanilla)
- Disc-change: no Ask UI, **black + no sound** (script not reaching post-DSKCG music/jump)

## v6

DSKCG force-complete with stack + null-safe entity clear + PC+=2. MOVIE still vanilla.
