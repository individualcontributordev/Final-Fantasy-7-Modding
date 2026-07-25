# In-place FORCE stub — assembled (88-byte slot)

**Date:** 2026-07-25  
**Confidence:** likely  
**Related:** [danger-add-block-size](2026-07-25-danger-add-block-size.md), [dat-71e38-71e3c-xrefs](2026-07-25-dat-71e38-71e3c-xrefs.md)

## Slot

Overwrite `0x800ABB7C`–`0x800ABBD4` (88 bytes). Fall through to `jal increment_step_id`.

## Logic (branchless)

```
entropy = COP0 Count & 0xff
force   = (entropy < g_enemy_lure) ? 1 : 0
g_danger = -force   # halfword store → 0x0000 or 0xFFFF
```

Each check overwrites Danger **before** the threshold read → no field-enter clear needed.

## Instructions

| VA | Word (LE display) | Asm |
|----|-------------------|-----|
| `800ABB7C` | `00 48 02 40` | `mfc0 v0, Count` |
| `800ABB80` | `06 80 01 3c` | `lui at, 0x8006` |
| `800ABB84` | `19 2f 23 90` | `lbu v1, 0x2f19(at)` ; `g_enemy_lure` |
| `800ABB88` | `ff 00 42 30` | `andi v0, v0, 0xff` |
| `800ABB8C` | `2b 10 43 00` | `sltu v0, v0, v1` |
| `800ABB90` | `23 10 02 00` | `subu v0, zero, v0` |
| `800ABB94` | `07 80 01 3c` | `lui at, 0x8007` |
| `800ABB98` | `3c 17 22 a4` | `sh v0, 0x173c(at)` ; `g_danger` |
| `800ABB9C`–`800ABBD0` | `00 00 00 00` ×14 | `nop` |

## Byte blob (88 bytes, Listing order)

```
00 48 02 40 06 80 01 3c 19 2f 23 90 ff 00 42 30
2b 10 43 00 23 10 02 00 07 80 01 3c 3c 17 22 a4
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00
```

## Follow-ups

- [ ] Patch FIELD in Ghidra / binary at `0x800ABB7C`
- [ ] Confirm Listing disassembly matches table
- [ ] DuckStation playtest FORCE rate + Aps preempt
