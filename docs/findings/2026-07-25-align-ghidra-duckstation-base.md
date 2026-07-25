# Ghidra / DuckStation base align @ 0x800A0000

**Date:** 2026-07-25  
**Confidence:** confirmed (DuckStation); Ghidra answers still blank in report

## DuckStation

| Address | Observed | Verdict |
|---------|----------|---------|
| `0x800AB9C8` | `3C02800A` = `lui v0,0x800a` | **match** `increment_step_id` |
| `0x800E0638` | word `6CEECAB1` (data / UNKNOWN) | **match** table head `B1 CA EE 6C` in LE memory |

FIELD.BIN is loaded at **`0x800A0000`** in the running game.

## Ghidra

Report left `Ghidra_0x800AB9C8_lui_lbu` / `Ghidra_0x800E0638_rng_table` empty — still need fresh import at base `0x800A0000` confirmed in GUI.
