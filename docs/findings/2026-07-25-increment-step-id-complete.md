# increment_step_id complete + FIELD.BIN load base

**Date:** 2026-07-25  
**Confidence:** confirmed (function); likely (load base `0x800A0000`)

## Full function (Ghidra listing, import base `0x80000000`)

Entry labeled `increment_step_id` at **`0x8000B9C8`** (file `0xB9C8`):

1. Load StepID (`0x8009C540` via `lui 0x800a` / `-0x3ac0`), increment, store  
2. If StepID == 0 after inc: Offset (`0x8009AD2C`) += 13  
3. Table lookup:
   - `lui at,0x800e` ; `addiu at,at,0x638` → **`0x800E0638`**
   - `addu at,at,v1` (index = StepID)
   - `lbu v0,0(at)`
4. `lbu` Offset; `subu v0,v0,v1`; `andi v0,0xff`; `jr ra`

Matches wiki: `return (RNG_TABLE[stepid] - offset) & 0xff`.

## Load base correction

Table file offset `0x40638` + base **`0x800A0000`** = **`0x800E0638`** (matches code).  
With import base `0x80000000`, Ghidra shows table at `0x80040638` and function at `0x8000B9C8`.

| File offset | Ghidra @ base 0x80000000 | Likely real VA @ base 0x800A0000 |
|-------------|--------------------------|----------------------------------|
| `0xB9C8` | `0x8000B9C8` | `0x800AB9C8` |
| `0x40638` | `0x80040638` | `0x800E0638` |

Real VA ≈ Ghidra_VA + **`0xA0000`** while project stays on wrong base. Prefer re-import at `0x800A0000` before DuckStation PC matching.

## Next

- Xrefs **to** `increment_step_id` → `encounter_check`  
- Same pattern for `increment_formation` / Danger  
- Field-load reseed hook later  
