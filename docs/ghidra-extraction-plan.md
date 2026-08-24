# FF7 PSX - Complete Ghidra Extraction Plan

> **Stale status note (verified 2026-08-24):** The "🔲 TODO" / "Next Steps"
> markers below are outdated. `scripts/ghidra/*.json` now contains
> functions+symbols for all of FIELD, BATTLE, BATRES, WORLD, and
> SCUS_941.63 — see `docs/06-ghidra-automation.md` for the current
> extraction workflow. This file is left as the original planning record.

## Files Containing Executable Code (Priority Order)

### Tier 1: Core Gameplay Modules (Essential for Modding)

| File | Disc | Base Address | Size (approx) | Purpose | Status |
|------|------|--------------|---------------|---------|--------|
| **FIELD.BIN** | All | `0x800A0000` | 264 KB | Field engine, encounters, scripts | ✅ Extracted |
| **BATTLE/BATTLE.X** | All | `0x800A0000` | 342 KB | Battle engine, attacks, AI | 🔲 TODO |
| **BATTLE/BATRES.X** | All | `0x801B0000` | 6 KB | Victory fanfare, rewards | 🔲 TODO |
| **WORLD.BIN** | All | Unknown | Unknown | World map engine, movement | 🔲 TODO |

### Tier 2: Initialization & Supporting Modules

| File | Disc | Base Address | Size | Purpose | Priority |
|------|------|--------------|------|---------|----------|
| **SCUS_941.63** | All | `0x80010000` | ~400 KB | Main kernel, module loader | Medium |
| **BATTLE/BATINI.X** | All | Unknown | 10 KB | Battle initialization | Low |
| **BATTLE/BROM.X** | All | Unknown | Unknown | Battle ROM routines | Low |

### Tier 3: Data Files (Mostly Non-Executable)

| File | Disc | Format | Purpose | Extract? |
|------|------|--------|---------|----------|
| **INIT/KERNEL.BIN** | All | 27 GZIP sections | Static data, text, item/materia/magic tables | Maybe (has some code) |
| **BATTLE/SCENE.BIN** | All | Custom | Enemy AI scripts, formations | Maybe (scripts) |
| **BATTLE/CO.BIN** | All | Unknown | Unknown battle component | TBD |

## Extraction Workflow

### Phase 1: Manual GUI Setup (One-Time Per File)

For each file above:

1. Extract from disc → decompress (if GZIPPS)
2. Import into Ghidra GUI with correct processor (MIPS:LE:32) and base address
3. Run Auto Analyze
4. Save project

### Phase 2: Automated Metadata Extraction

Run `ExtractFieldMetadata.java` on each file to get:
- Functions (name, address, size, callers)
- Symbols (labels, data references)

Output: `workspace/ghidra-analysis/<module>-functions.json`

### Phase 3: Cross-Module Reference Map

Build a **call graph** showing which modules call into each other:
- BATRES → BATTLE (victory calls into battle engine)
- FIELD → BATTLE (encounter triggers)
- All → SCUS (kernel services)

## Current Status

**Completed:**
- ✅ FIELD.BIN extracted (26 KB functions JSON)
- ✅ Java extraction script working
- ✅ Workflow documented in INSTRUCTIONS.md

**Next Steps:**
1. Import BATTLE.X, BATRES.X, WORLD.BIN into Ghidra GUI
2. Run batch extraction script (or manual per-file)
3. Build cross-module reference database

## Why This Matters for Single-Disc Mod

**Current patches:**
- FIELD.BIN → removed disc-ask opcodes ✅
- BATTLE.X → remapped 17 SNOVA LBAs ✅

**Future needs:**
- WORLD.BIN → world map might have disc checks
- BATRES.X → if victory logic references disc-specific data
- KERNEL.BIN → if item/materia tables differ per disc

**The metadata lets Agent:**
- Find all references to disc-related addresses
- Verify no hardcoded disc checks remain
- Plan new features (button combos, debug menus, etc.)

## Notes

- **SCENE.BIN** = mostly data (enemy formations, AI scripts), not a loadable module
- **KERNEL.BIN** = 27 sections, first 9 are data tables, rest is text
- **Base addresses** from `docs/ghidra-battle-overlays.md` and Qhimm research
- **GZIPPS format** = 8-byte header + gzip payload (decompress with `scripts/decompress_gzipps.py`)
