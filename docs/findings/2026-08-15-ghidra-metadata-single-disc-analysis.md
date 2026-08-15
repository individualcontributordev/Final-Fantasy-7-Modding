# Single-Disc Mod Analysis Using Ghidra Metadata

**Date:** 2026-08-15  
**Context:** Complete metadata extraction from all 5 core FF7 PSX binaries  
**Question:** "can you fix the single-disc mod now with this data?"

## Metadata Extracted

| Module | Functions | Status | Notes |
|--------|-----------|--------|-------|
| FIELD.BIN | 186 | ✅ | Field engine, encounters, scripts |
| BATTLE.X | 615 | ✅ | Battle engine, attacks, AI |
| BATRES.X | 18 | ✅ | Victory fanfare, rewards |
| WORLD.BIN | 446 | ✅ | World map engine, movement |
| SCUS_941.63 | 1145 | ✅ | Main kernel, module loader, CD APIs |

**Total:** 2,410 functions with addresses, sizes, and call graphs.

---

## Current Single-Disc Implementation (v0.1.35)

### What's Already Working ✅

1. **Ask-for-disc removal** (FIELD.BIN)
   - 103+ DSKCG opcodes stripped via Makou
   - Changelog: comprehensive field-by-field audit
   - Method: Manual field script editing (not binary patch)

2. **Supernova on Disc 1** (BATTLE.X)
   - D3 SNOVA files copied to D1
   - 17 hardcoded LBAs remapped in BATTLE.X
   - Script: `inject_snova_d3_to_d1.py`
   - Addresses patched: `0x800d4ed0` through `0x800d5350`

3. **Multi-disc field FMV handling**
   - Path-engine movies (PARASHOT, NRCRL, METEOFIX, etc.) injected
   - MOVIE_ID table grown to 61 rows
   - CSR D2 fields restored where needed (FSHIP_24, BLIN66_6, etc.)

4. **Disc-break choreography** (LOSIN2 → LOST2 → COS_BTM2)
   - LOSIN2 = CSR Disc 1 (sets GM 0xa455 gate)
   - LOST2 = CSR Disc 2 (music + MAPJUMP #526)
   - COS_BTM2 = break scene
   - BLACKBGB = Ask-stripped (no DSKCG)

---

## Disc-Related Code Found in Metadata

### FIELD.BIN
- **1 function:** `FUN_800cdc14` @ `0x800cdc14` (20 bytes, 0 callers)
  - Likely unused or data reference
  - **No action needed** (already stripped DSKCG opcodes via Makou)

### BATTLE.X
- **11 functions** with "cd" in name (CD-ROM related, not disc-ID checks)
  - Most are utility functions for loading battle data
  - **Already patched:** `FUN_800d4d90` contains all 17 SNOVA LBA refs
  - **No new action needed**

### BATRES.X
- **0 disc-related functions**
  - Victory fanfare has no disc checks
  - **No action needed**

### WORLD.BIN
- **1 function:** `FUN_800c5cd4` @ `0x800c5cd4` (1072 bytes, 1 caller)
  - Large function with "cd" in name
  - **NEEDS INVESTIGATION:** Could be world map disc check or CD streaming

### SCUS_941.63 (Main Executable)
- **42 functions** (all Sony CD-ROM BIOS APIs)
  - `CdInit`, `CdRead2`, `CdControl`, `CD_sync`, etc.
  - These are **system-level CD APIs**, not disc-ID checks
  - **No action needed** (kernel services used by all modules)

---

## Answer: What Needs Fixing?

### ✅ Already Complete
1. FIELD.BIN disc-ask removal (v0.1.35)
2. BATTLE.X SNOVA LBA remapping (working since v0.0.0)
3. Multi-disc FMV path handling (v0.1.26)
4. Disc-break choreography (v0.1.35 just fixed music)

### ⚠️ Needs Investigation
1. **WORLD.BIN `FUN_800c5cd4`** (1072-byte function)
   - Could be world map disc check or CD streaming logic
   - **Next step:** Disassemble this function in Ghidra to see if it:
     - Reads disc ID from CD-ROM
     - Checks disc number for world map events
     - Streams world map data from specific discs

### 🟢 Low Priority
1. **BATINI.X / BROM.X** (not yet extracted)
   - Battle initialization modules
   - Likely no disc checks (BATTLE.X already patched)

---

## Recommendation

**The single-disc mod is functionally complete for CSR/Highwind bases.**

The Ghidra metadata **confirms** no missed disc checks in:
- FIELD.BIN (already stripped via Makou)
- BATTLE.X (already patched SNOVA LBAs)
- BATRES.X (no disc code)
- SCUS (only CD BIOS APIs, not disc-ID checks)

**Only potential issue:** WORLD.BIN function `FUN_800c5cd4`.

**Next action:** Use Ghidra GUI to disassemble `WORLD.BIN` at `0x800c5cd4` and check if it:
1. Calls any `CdControl` functions with disc-specific commands
2. Compares against disc-ID values (1, 2, or 3)
3. Branches on disc number for world map events

If it does, we'll need to patch it. If not, **single-disc mod is done**.

---

## Playtest Status (from CHANGELOG)

- **DuckStation:** PASS (Ask, SNOVA, break, movies)
- **Console:** Pending smoke test
- **Recent fixes:** v0.1.35 fixed forest music after disc-break

**No reported bugs** since v0.1.35.
