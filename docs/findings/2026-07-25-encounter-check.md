# encounter_check found (dual RNG + Danger compare)

**Date:** 2026-07-25  
**Confidence:** confirmed (body) / likely-wrong-start (entry)  
**Related:** [01-encounter-system.md](../01-encounter-system.md), [increment-step-id-xrefs](2026-07-25-increment-step-id-xrefs.md)

## Summary

Ghidra has a function labeled `encounter_check` that calls `increment_step_id` twice and compares against Danger at `0x8007173C`.

## Discovery

Ghidra listing (user paste) shows:

| Address | Instruction | Role |
|---------|-------------|------|
| `0x800ABBD4` | `jal increment_step_id` | Preempt roll |
| `0x800ABBE0` | `lbu` `DAT_80062f1b` | Preempt threshold (mask `0x7f`) |
| `0x800ABBFC` / `0x800ABC0C` | `sb` `DAT_800716d0` | Flag set to `4` or `0` |
| `0x800ABC10` | `jal increment_step_id` | Danger-threshold roll |
| `0x800ABC1C` | `lhu` **`DAT_8007173c`** | **Danger** (wiki `0x8007173C`) |

Decompiler threshold (simplified):

```
roll2 = increment_step_id() & 0xff
if (roll2 < (Danger * DAT_80062f19) >> 12)
  → trigger battle / pick formation
```

Formation path calls `FUN_800a1498`, sets `DAT_8009abf5 = 2`, `DAT_8007ebc8 = 1`, then `FUN_800aba34()` (likely formation RNG / slot pick).

## Important corrections

1. **Danger is present.** User note said “cannot find danger”, but `DAT_8007173c` / `_DAT_8007173c` **is** Danger. Rename in Ghidra: `L` → `g_danger`.
2. **Function start is probably wrong.** Ghidra entry is at the **first `jal`** (`0x800ABBD4`). Decompiler has `unaff_s1` (s1 used, never set) → real prologue / map-table pointer load is **above** this address. Re-find entry, then re-create the function (`F`).

## Why it matters

Confirms the wiki dual-roll model in our FIELD.BIN. Next we need the true function entry and Danger **growth** (add to Danger), which may be earlier in this function or a sibling called each movement tick.

## Follow-ups

- [ ] Find true `encounter_check` entry (scroll up from `0x800ABBD4`; fix `unaff_s1`)
- [ ] Rename `DAT_8007173c` → `g_danger`
- [ ] Identify `DAT_80062f19` / `DAT_80062f1b` (rate / preempt)
- [ ] Label `FUN_800aba34` (formation roll?)
- [ ] Find where Danger is **incremented** (add, not just compared)
