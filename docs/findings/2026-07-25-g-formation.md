# g_formation renamed via lbu xref

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [increment-formation](2026-07-25-increment-formation.md)

## Summary

Formation counter labeled **`g_formation`** (wiki/RAM `0x80071C20`) via `lbu` at `0x800ABA38`.

## Evidence

```
800aba38  lbu v0,offset g_formation(v0)
800aba40  addiu +1
800aba48  sb  … g_formation
```

Decompiler: `g_formation = g_formation + 1; return g_field_rng_table[g_formation];`
