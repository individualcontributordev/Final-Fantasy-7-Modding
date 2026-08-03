# No-disc-swap — Ask for disc inventory (pristine D1)

**Date:** 2026-08-02
**Confidence:** confirmed (Makou Find All screenshots + operator notes)
**Sources:** `docs/INSTRUCTIONS.md` @ 56df347; Find All on Unmodified D1

## Summary

Every `Ask for disc N` on pristine Disc 1 sits in **three field maps** only.
The live story hub is **`blackbgb` (#103)**. The other two have **no inbound
map jumps from other D1 scripts** (operator); treat as secondary / entry hubs.

## Maps

| Map | Field # | Role on D1 |
|-----|---------|------------|
| `blackbgb` | 103 | **Active hub.** Many maps jump here. Also bike mini-game return target. Holds story disc 2/3 asks in `S0 - Main` (`init`). |
| `blackbge` | 106 | One ask (disc 2). **No D1 inbound jumps** found. |
| `blackbg3` | 95 | Many asks in talk scripts (`p7`/`p8`). **No D1 inbound jumps** found. |

Inbound jumps **to** `blackbgb` (separate Find All) include e.g. `frst_1`,
`rcktin5`, `blin1`, `losin2`, `blackbgd`, bike end from `blackbg3`, etc.

## Ask for disc — full hit list (Makou Find All)

### `blackbge` (#106)

| Group | Script | Line | Ask |
|-------|--------|------|-----|
| AD | Script 4 | 2 | disc **2** |

### `blackbgb` (#103) — priority for no-disc-swap

| Group | Script | Line | Ask |
|-------|--------|------|-----|
| init | S0 - Main | 43 | disc **3** |
| init | S0 - Main | 64 | disc **3** |
| init | S0 - Main | 73 | disc **2** |
| init | S0 - Main | 95 | disc **2** |

### `blackbg3` (#95)

| Group | Script | Line | Ask |
|-------|--------|------|-----|
| p8 | S1 - Talk | 27, 33, 42, 52, 58, 87, 100 | disc **1** (×7) |
| p8 | S1 - Talk | 113, 132, 166, 178, 185, 207 | disc **2** (×6) |
| p7 | S1 - Talk | 25 | disc **1** (×1) |

## Counts (D1 Find All)

| Ask | Count |
|-----|------:|
| disc 1 | 8 |
| disc 2 | 9 |
| disc 3 | 2 |
| **Total** | **19** |

## Mod design notes

1. **Must fix first:** `blackbgb` / `init` / `S0 - Main` — four asks (2× disc2, 2× disc3) on the map everyone jumps into. Earlier paste already showed post-ask jumps to `lost2` (#634) and `las0_1` (#744).
2. **Still patch for completeness:** `blackbge`, `blackbg3` (orphaned on D1 graph but present on the shared FIELD set; may matter if something loads them or for D2/D3 mirrors).
3. **Do not confuse** with other maps that only **jump to blackbgb** — those are not Ask sites.
4. Multi-disc `Set next movie` still optional/unlisted this pass.

## Next

Dump full `blackbgb` S0-Main disc branches (conditions + jump targets) for a minimal pristine edit plan.
