# increment_step_id has 2 callers (encounter check)

**Date:** 2026-07-25  
**Confidence:** confirmed

## Xrefs (Ghidra @ base 0x800A0000)

| From | Type |
|------|------|
| `0x800ABBD4` | `jal increment_step_id` |
| `0x800ABC10` | `jal increment_step_id` |

Matches wiki: encounter loop calls `increment_step_id` **twice** (preempt + threshold). Both should sit in one function → label **`encounter_check`**.
