# g_enemy_lure has no writers in FIELD.BIN

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [g-enemy-lure](2026-07-25-g-enemy-lure.md)

## Summary

Ghidra xref list for `g_enemy_lure` (`0x80062F19`) in FIELD.BIN:

| Address | Access |
|---------|--------|
| `0x800ABC24` | `lbu` READ (threshold compare) |

**No WRITE xrefs** in this module. Value is set elsewhere (kernel / menu / battle overlay — RAM below FIELD base `0x800A0000`).

## Implications for MAX Danger

Default lure unknown from FIELD alone. Even if lure &lt; 17:

- FORCE sets `g_danger = 0xFFFF` and it **stays** until battle clear or field-enter clear
- Later checks keep comparing until a roll succeeds
- Low lure → may take a few extra checks, not “never fight”

Still scale FORCE **probability** by lure so Lure/Away materia matter.

## Follow-ups

- [ ] Optional: DuckStation watch `0x80062F19` with/without Enemy Lure
- [ ] Pick entropy source for FORCE roll
- [ ] Assemble in-place stub
