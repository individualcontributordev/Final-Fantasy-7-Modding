# increment_formation @ 0x800ABA34

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [encounter-check-renamed](2026-07-25-encounter-check-renamed.md)

## Summary

`FUN_800aba34` is **`increment_formation`**: bumps formation byte, returns `g_field_rng_table[formation]`.

## Discovery

```
800aba34  lbu DAT_80071c20   // Formation @ 0x80071C20
800aba40  addiu +1
800aba48  sb
800aba5c  table base 0x800E0638 (g_field_rng_table)
800aba64  lbu table[formation]
```

Decompiler:

```
DAT_80071c20 = DAT_80071c20 + 1;
return (&g_field_rng_table)[DAT_80071c20];
```

Xrefs from `encounter_check`: `0x800ABC68`, `0x800ABDF4`, `0x800ABE9C`.

Note: no Offset subtract (unlike `increment_step_id`) — matches wiki formation helper.

## Follow-ups

- [ ] Rename `DAT_80071c20` → `g_formation`
- [ ] Label caller `FUN_800a65a4`
- [ ] Find `field_map_init` (reseed hook)
