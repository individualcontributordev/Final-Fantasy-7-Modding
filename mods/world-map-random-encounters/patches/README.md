# Patch: world-map FORCE encounter stub (RCnt2)

**VA base:** `0x800A0000` (`WORLD.BIN.dec`)

## Window

| Dec offset | VA | Bytes | Meaning |
|------------|-----|-------|---------|
| `0x17DB4` | `0x800B7DB4` | 104 | Danger += → RCnt2 FORCE (`stub-7db4-rateXX.hex`) |
| `0x17E1C` | `0x800B7E1C` | 4 | must stay `jal WorldRand` (`jal-7e1c.hex`) |

## Logic

```
entropy = RCnt2 & 0xff
thresh  = g_enemy_lure scaled (25/50/75%)
g_world_danger = ((entropy < thresh) ? 0xFFFF : 0)
→ jal WorldRand
→ battle if WorldRand() < (g_world_danger >> 8) && encounters enabled
```

Same density presets as Field (Light / Standard / Dense).

## Apply

```bash
python scripts/decompress_gzipps.py workspace/iso-extract/WORLD.BIN workspace/iso-extract/WORLD.BIN.dec
cp workspace/iso-extract/WORLD.BIN.dec workspace/iso-extract/WORLD.BIN.dec.patched
python mods/world-map-random-encounters/scripts/apply_world_force_stub.py \
  workspace/iso-extract/WORLD.BIN.dec.patched --density standard
```

Then recompress + CDmage import (same GZIPPS path as Field).

## Runtime watches (2026-07-30)

- `g_world_danger` @ `0x80116284` (word). Each check the stub stores **only** `0` or `0xFFFF`. `FFFF` may last one check; a later miss overwrites with `0` (normal — not a bug).
- Break: execute `0x800B7DE0` (FORCE ori) / `0x800B7DF4` (sw), or **write** `0x80116284`. Do not execute-break data RAM.
- Observed mid-values such as `0x40` at the same address are **not** stub FORCE outputs. Full playtest: `docs/findings/2026-07-30-world-light-runtime-verify.md`.
