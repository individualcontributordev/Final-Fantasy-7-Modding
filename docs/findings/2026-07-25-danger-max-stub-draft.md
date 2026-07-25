# In-place FORCE stub — RCnt2 entropy (88-byte slot)

**Date:** 2026-07-25  
**Confidence:** likely  
**Related:** [playtest-always-force](2026-07-25-playtest-always-force.md), [danger-add-block-size](2026-07-25-danger-add-block-size.md)

## Slot

Overwrite `0x800ABB7C`–`0x800ABBD4` (88 bytes). Keep `jal increment_step_id` @ `0x800ABBD4`.

## Logic

```
entropy = RCnt2 @ 0x1F801120   # system root counter (not COP0 Count)
force   = ((entropy & 0xff) < g_enemy_lure) ? 1 : 0
g_danger = -force               # halfword → 0 or 0xFFFF
```

## Instructions

| VA | Bytes LE | Asm |
|----|----------|-----|
| `800ABB7C` | `80 1f 01 3c` | `lui at,0x1f80` |
| `800ABB80` | `20 11 22 8c` | `lw v0,0x1120(at)` |
| `800ABB84` | `00 00 00 00` | `nop` (load delay) |
| `800ABB88` | `06 80 01 3c` | `lui at,0x8006` |
| `800ABB8C` | `19 2f 23 90` | `lbu v1,0x2f19(at)` |
| `800ABB90` | `ff 00 42 30` | `andi v0,v0,0xff` |
| `800ABB94` | `2b 10 43 00` | `sltu v0,v0,v1` |
| `800ABB98` | `23 10 02 00` | `subu v0,zero,v0` |
| `800ABB9C` | `07 80 01 3c` | `lui at,0x8007` |
| `800ABBA0` | `3c 17 22 a4` | `sh v0,0x173c(at)` |
| `800ABBA4`–`800ABBD0` | nop ×12 | |

## Byte blob (88)

```
80 1f 01 3c 20 11 22 8c 00 00 00 00 06 80 01 3c
19 2f 23 90 ff 00 42 30 2b 10 43 00 23 10 02 00
07 80 01 3c 3c 17 22 a4 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00
```
