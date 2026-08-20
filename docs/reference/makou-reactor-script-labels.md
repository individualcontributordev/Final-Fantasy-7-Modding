# Makou Reactor Script Labels

**Source:** `makoureactor/src/core/field/GrpScript.cpp` (`GrpScript::scriptName`), read on 2026-08-20.

Maps a field entity's raw script index (`script_slot` in
`docs/reference/field-scripts-database.md`, same 0-based index our
`scripts/field_dat.py` `ScriptSlot.slot` uses) to the label Makou Reactor
shows in its script list UI.

## Mapping

| `scriptID` | Label shown in Makou Reactor | Notes |
|---|---|---|
| 0 | `S0 - Init` | Always, all entity types |
| 1 | `S0 - Main` | Always, all entity types (no type branch) |
| 2 | `S1 - Talk` | Only if entity type = **Model** |
| 2 | `S1 - [OK]` | Only if entity type = **Location** (walkmesh line) |
| 3 | `S2 - Contact` | Only if type = **Model** |
| 3 | `S2 - Move` | Only if type = **Location** |
| 4 | `S3 - Move` | Only if type = **Location** |
| 5 | `S4 - Go` | Only if type = **Location** |
| 6 | `S5 - Go 1x` | Only if type = **Location** |
| 7 | `S6 - Go away` | Only if type = **Location** |
| other / no type match | `Script %1` where `%1 = scriptID - 1` | Fallback, e.g. scriptID 9 → `Script 8` |

Entity type (`Model` / `Location` / `Animation` / `Director` / `NoType`) is
detected from the first opcode in script slot 0 (`GrpScript::detectType`):

- `PC` or `CHAR_` opcode → **Model**
- `LINE` opcode → **Location**
- `BGPDH`/`BGSCR`/`BGON`/`BGOFF`/`BGROL`/`BGROL2`/`BGCLR` → **Animation** (no per-slot script names beyond S0/S1 — falls to `Script %1`)
- `MPNAM` → **Director** (no per-slot script names beyond S0/S1 — falls to `Script %1`)

## Practical examples (COS_BTM2 dual-edit slots)

- `AD`, slot 0 → **AD, S0 - Init**
- `BALLET`, slot 1 → **BALLET, S0 - Main**
- `EARITH`, slot 1 → **EARITH, S0 - Main**
- `RED`, slot 1 → **RED, S0 - Main**
- `TIFA`, slot 1 → **TIFA, S0 - Main**

## Caveat: `GrpScript::toByteArray`

For `scriptID == 0`, Makou concatenates the raw bytes of internal slots 0
and 1 (`_scripts.at(0) + _scripts.at(1)`) when exporting/comparing raw
script bytes — i.e. "Init" as exported includes what our tooling calls slot
0. For `scriptID >= 1`, it returns `_scripts.at(scriptID + 1)` (internal
storage is offset by one slot vs. the exposed `scriptID`). This offset is
internal to Makou's `GrpScript` storage class and does not change the
`scriptID`-to-label mapping above, which is what's shown in the UI and is
what our `ScriptSlot.slot` values correspond to.
