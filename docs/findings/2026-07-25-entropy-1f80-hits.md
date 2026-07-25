# FIELD.BIN has many 0x1f80 IO references

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [entropy-search-empty](2026-07-25-entropy-search-empty.md)

## Summary

Scalar search `0x1f80` returns **many** hits (GPU/SPU/DMA-style code). Full `0x1f801110/120` had no hits earlier — timers may still be `lui 0x1f80` + separate `ori`/`addiu` offset.

## First candidates to inspect

| Function | Why |
|----------|-----|
| `FUN_800a14d8` | Few hits @ `0x800A14F0` — small, check if RCnt |
| `FUN_800a8968` | Next cluster |

Look for offsets **`0x110` / `0x120` / `0x100`–`0x128`** after `lui …,0x1f80` (root counter block).

## Follow-ups

- [ ] Disassemble `FUN_800a14d8` IO offsets
- [ ] If not timer: pick mix entropy or DuckStation frame counter
