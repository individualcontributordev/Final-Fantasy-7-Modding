# world_lure_factor @ 0x800B7B54; g_world_danger labeled

**Date:** 2026-07-28  
**Confidence:** confirmed  
**Related:** [world-danger](2026-07-28-world-danger.md)

## Labels

| Symbol | VA | Notes |
|--------|-----|--------|
| `g_world_danger` | `0x80116284` | renamed via `sw` @ `0x800B7E18` |
| `world_lure_factor` | `0x800B7B54` | was `FUN_800b7b54` |
| lure byte | `DAT_80062f19` | same as Field `g_enemy_lure` |

## `world_lure_factor`

```c
uVar1 = DAT_80062f19;          // Enemy Lure
if (0x10 < uVar1) uVar1 <<= 1; // wiki: doubles when > 16
return uVar1;
```

Danger += `(world_lure_factor() << 10) / rate` → at default lure 16: `16384/rate` per check.

## Next

Assemble RCnt2 FORCE stub over Danger += (`0x800B7DBC`–`0x800B7E18` or from `0x800B7DB4` to cover rate==0 `+=0x7FFF` path).
