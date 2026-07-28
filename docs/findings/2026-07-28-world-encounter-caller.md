# World encounter caller = FUN_800b7c7c (RA before battle)

**Date:** 2026-07-28  
**Confidence:** confirmed  
**Related:** [worldrand](2026-07-28-worldrand.md), [worldrand-break-partial](2026-07-28-worldrand-break-partial.md)

## DuckStation RA samples (break @ `WorldRand` `0x800ADFC0`)

| RA (return) | Implied `jal` (RA−8) | Function |
|-------------|----------------------|----------|
| `0x800A300C` (many) | `0x800A3004` | `FUN_800a21b4` — movement scramble |
| `0x800B0B64` / `0x800B0B7C` | `0x800B0B5C` / `0x800B0B74` | `FUN_800b0810` |
| `0x800B7E24` … `0x800B81CC` | `0x800B7E1C` … `0x800B81C4` | **`FUN_800b7c7c`** (8× `WorldRand`) |
| `0x8003CF74` (once) | outside WORLD overlay | ignore |

**`ra_last_before_battle`:** `0x800B81CC` → `jal WorldRand` @ **`0x800B81C4`** inside **`FUN_800b7c7c`**.

Burst of `FUN_800b7c7c` call sites immediately before battle = encounter / formation path.

## Next

Open `0x800B7C7C`, rename `world_encounter_check`, locate Danger += and the compare that uses `WorldRand` (esp. near `0x800B81C4`).
