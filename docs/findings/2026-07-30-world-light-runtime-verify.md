# World Light runtime verify (DuckStation + CE)

**Date:** 2026-07-30  
**Confidence:** confirmed  
**Status:** promoted  
**Related:** [world-danger](2026-07-28-world-danger.md), [world-force-playtest](2026-07-28-world-force-playtest.md), mods/world-map-random-encounters/patches/README.md

## Summary

Builder zip (Unmodified + Field Light + World Light) PASSed on-disk verification; world FORCE stub is live at runtime; stub stores only 0 or 0xFFFF to g_world_danger; FFFF is often a single check then cleared by a later miss store — that is expected, not a bug. Observed 0x40 at the same address is real but is not a stub FORCE value.

## Context

Human reported field Danger then world watch values of 0x40 / 64 decimal. Needed to prove world Light on the bootable zip and explain DuckStation / Cheat Engine watches.

## Discovery

### Builder / disc

- Builder zip: clean + field-encounter-25-v0.1.2 + world-encounter-25-v0.1.0
- scripts/verify_built_disc.py with matching --base / --addon / --disc → PASS
- APPLIED: Field Light + World Light; FIELD stub@0xbb7c=YES; WORLD stub@0x17db4=YES

### Code (DuckStation CPU debugger)

| VA | Meaning |
|----|---------|
| 0x800B7DB4 | World stub entry (dec+0x17DB4): lui at,0x1f80 / lw RCnt2 0x1F801120 |
| 0x800B7DC4 | lbu g_enemy_lure @ 0x80062F19 |
| 0x800B7DCC | Light: srl v1,v1,2 (lure/4) |
| 0x800B7DE0 | FORCE: ori v0, zero, 0xffff |
| 0x800B7DEC | Miss: addu v0, zero, zero |
| 0x800B7DF4 | sw v0, 0x6284(at) → 0x80116284 (g_world_danger) |

Early freeze at 0x800B7DB4 showed vanilla bne/lh (before world load). Later freezes show stub. Confirm on world map after WORLD.BIN load.

### RAM / Cheat Engine

| Symbol | PS1 VA | CE guest offset | Size |
|--------|--------|-----------------|------|
| g_world_danger | 0x80116284 | +116284 | 4 bytes hex |
| g_danger (field) | 0x8007173C | +7173C | 2 bytes |
| g_enemy_lure | 0x80062F19 | +62F19 | 1 byte (often 0x10) |
| g_world_rand_index | 0x8010AE58 | +10AE58 | 4 bytes |

Host base example: duckstation-qt-x64-ReleaseLTCG.exe+7F1600 (session-specific). Guest offsets are stable relative to RDRAM.

### Values at g_world_danger

| Value | Meaning |
|-------|---------|
| 0 | Miss path, or later miss store overwrote FORCE |
| 0xFFFF | FORCE hit — confirmed on BP (v0=FFFF, RAM FF FF 00 00) |
| 0x40 (64) | Seen once at correct address — not written by stub |

Stub only stores 0 or 0xFFFF (stub-7db4-rate25.hex). FFFF often lasts one check; next miss stores 0. CE can miss the flash without breakpoints. 0x40 is not half-cleared FFFF.

### Breakpoints that worked

| Address | Type |
|---------|------|
| 0x800B7DE0 | Execute (FORCE ori) |
| 0x800B7DF4 | Execute (sw) |
| 0x80116284 | Write (not Execute) |

Battle still occurred after FORCE proof (world encounter → battle screen).

## How we found it

verify_builder_config / verify_built_disc; DuckStation debugger; Cheat Engine; docs/image-1.png .. image-3.png.

## Why it matters

End-to-end proof of shipped World Light; watch/BP recipe; stop treating 0x40 as a density bug.

## Follow-ups

- [ ] Optional: xref other writers to g_world_danger if 0x40 reappears outside battle
- [ ] Keep 1-2 proof screenshots or delete playtest image pile after promotion

## Sources

- mods/world-map-random-encounters/patches/stub-7db4-rate25.hex
- docs/findings/2026-07-28-world-danger.md
- session 2026-07-30 builder verify + runtime screenshots
