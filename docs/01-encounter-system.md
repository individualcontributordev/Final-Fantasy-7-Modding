# FF7 PS1 Field Encounter System

Reference for reverse engineering in Ghidra. Sources: FF7 speedrun wiki, TASVideos
writeups, Qhimm forums, ff7tk source.

## Encounter check loop (every ~8 movement frames)

While Cloud moves on a hostile field with encounters enabled:

1. **Step fraction** += 32; wraps at 256
2. On wrap:
   - **Danger** += `2 * FieldScale * (4 if running, 1 if walking) / EncounterRate`
   - Call `increment_step_id()` → preempt roll
   - Call `increment_step_id()` again → danger threshold roll
   - If Danger ≥ threshold → battle; Danger resets to 0
   - Formation RNG picks enemy set (separate counter)

## `increment_step_id()` (pseudocode)

```
stepid = stepid + 1
if stepid == 0:          // wrapped 255 → 0
    offset = offset + 13
return RNG_TABLE[stepid] - offset   // mod 256 arithmetic
```

## `increment_formation()` (pseudocode)

```
formation = formation + 1
return RNG_TABLE[formation]
```

Formation value is divided by 4 to get a 0–63 roll for standard/special slot selection.

## RNG table (256 bytes, fixed in ROM/RAM)

First bytes: `B1 CA EE 6C 5A 71 2E 55 D6 00 CC 99 90 6B 7D EB 4F A0 …`

Full table in [FF7 speedrun wiki — Field map encounter mechanics](https://ff7speedruns.com/index.php/Field_map_encounter_mechanics).

## RAM addresses (PS1, base 0x80000000)

Emulator "address" column is often offset from 0x80000000.

| Variable | PS1 address | Emulator offset | Size |
|----------|-------------|-----------------|------|
| Danger | `0x8007173C` | `0x7173C` | 2 bytes |
| Formation | `0x80071C20` | `0x71C20` | 1 byte |
| StepID | `0x8009C540` | `0x9C540` | 1 byte |
| Offset | `0x8009AD2C` | `0x9AD2C` | 1 byte |
| Step fraction | `0x8009C6D8` | `0x9C6D8` | 1–2 bytes |

### Confirmed in FIELD.BIN.dec (US) — Ghidra

`increment_step_id` at Ghidra **`0x8000B9C8`** (import base `0x80000000`; likely real VA **`0x800AB9C8`** if module base is `0x800A0000`).

Access pattern:

- StepID: `lui …, 0x800a` + `lbu/sb …, -0x3ac0(…)` → `0x8009C540`
- Offset: `lui …, 0x800a` + `lbu/sb …, -0x52d4(…)` → `0x8009AD2C`
- On StepID wrap to 0: Offset += `0xd` (13)
- Table: `lui …, 0x800e` + `0x638` → **`0x800E0638`** (file `0x40638` at module base `0x800A0000`), index by StepID, subtract Offset, `& 0xff`

See [findings/2026-07-25-increment-step-id-complete.md](findings/2026-07-25-increment-step-id-complete.md).

## Per-map data (editable in Makou, not sufficient alone)

Stored in each field `.DAT` encounter section (48 bytes, two tables):

- `enabled` — 0 = no random battles
- `rate` — lower byte = **more** battles (inverse intuition)
- Battle IDs and probability weights for standard (6) and special (4) slots

Field **scale** (default 512) is in section 1 of the `.DAT` and affects Danger growth.

## What we will patch

| Component | File | Change |
|-----------|------|--------|
| Encounter timing + formation RNG | `FIELD.BIN` | Reseed on field load |
| World map encounters | `WORLD.BIN` | Same idea (later) |
| Per-map battle tables | `*.DAT` | No change needed |

## Separate RNG systems (do not confuse)

| System | Variables | Used for |
|--------|-----------|----------|
| Encounter RNG | StepID, Offset, Formation | Battle timing + enemy pick |
| Field script RNG | List (index), Stone (increment) | Opcodes, minigames, Bone Village dig |

Makou's `RANDOM` script opcode affects field script RNG only.
