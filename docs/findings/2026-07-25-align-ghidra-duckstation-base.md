# Ghidra / DuckStation base align @ 0x800A0000

**Date:** 2026-07-25  
**Confidence:** confirmed

## DuckStation

| Address | Observed | Verdict |
|---------|----------|---------|
| `0x800AB9C8` | `3C02800A` = `lui v0,0x800a` | match `increment_step_id` |
| `0x800E0638` | word `6CEECAB1` (data) | match table head `B1 CA EE 6C` LE |

## Ghidra

User confirmed re-import / checks at base **`0x800A0000`**: `0x800AB9C8` lui/lbu, `0x800E0638` RNG table, labels applied.

## Canonical addresses going forward

| Symbol | VA |
|--------|-----|
| FIELD.BIN base | `0x800A0000` |
| `increment_step_id` | `0x800AB9C8` |
| `g_field_rng_table` | `0x800E0638` |
| `encounter_check` | `0x800ABA70` |
| Danger / `g_danger` | `0x8007173C` |
| Step fraction (`g_step_fraction`) | `0x8009C6D8` |
| `increment_formation` | `0x800ABA34` |
| Formation (`g_formation`) | `0x80071C20` |
| StepID | `0x8009C540` |
| Offset | `0x8009AD2C` |
