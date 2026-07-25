# Found increment_step_id at ~0x8000B9C8

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Source:** Ghidra listing in `docs/windows-last-output.txt`

## Why scalars missed StepID

Code uses **`lui reg, 0x800a`** then **`lbu/sb …, -0x3ac0(reg)`**, not `lui 0x8009` + `0xc540`.

`0x800A0000 + (-0x3AC0) = 0x8009C540` (StepID).  
Offset: `lui 0x800a` + `-0x52d4` → `0x8009AD2C`.

## Disassembly (excerpt)

| VA | Instruction | Meaning |
|----|-------------|---------|
| `0x8000B9C8` | `lui v0,0x800a` | |
| `0x8000B9CC` | `lbu v0,-0x3ac0(v0)` | load StepID |
| `0x8000B9D4` | `addiu v0,v0,0x1` | StepID++ |
| `0x8000B9D8` | `lui at,0x800a` | |
| `0x8000B9DC` | `sb v0,-0x3ac0(at)` | store StepID |
| `0x8000B9E0` | `lui v1,0x800a` | |
| `0x8000B9E4` | `lbu v1,-0x3ac0(v1)` | reload StepID |
| `0x8000B9EC` | `bne v1,zero,…` | if non-zero after wrap check, skip |
| `0x8000B9F8` | `lbu v0,-0x52d4(v0)` | load Offset |
| `0x8000BA00` | `addiu v0,v0,0xd` | Offset += 13 |
| `0x8000BA08` | `sb … -0x52d4` | store Offset |

Matches wiki `increment_step_id` (wrap → Offset+=13).

## Labels to apply

- Function containing this: `increment_step_id`
- `DAT_8009c540` → `g_step_id` (if not already)
- `DAT_8009ad2c` → `g_offset`
