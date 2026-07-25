# field_map_init renamed @ 0x800BA534

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [field-map-setup](2026-07-25-field-map-setup.md)

## Summary

`FUN_800ba534` renamed to **`field_map_init`** @ `0x800BA534` (called from `field_main_loop` @ `0x800A1E40`).

## Evidence

```
field_map_init  XREF[1]: field_main_loop:800a1e40(c)
800ba534  addiu sp,sp,-0x18
```

## Hook plan (locked)

| Change | Site |
|--------|------|
| `g_danger = 0` on field enter | `field_map_init` entry and/or `LAB_800a1dc8` (`0x800A1DC8`) |
| Replace Danger `+=` with MAX RNG | `encounter_check` `0x800ABB7C`–`0x800ABBD0` |
| Keep StepID/Offset preempt | dual `jal increment_step_id` unchanged |
| Post-battle Danger = 0 | already in `field_main_loop` — leave it |

## Follow-ups

- [ ] Find code cave for MAX-RNG stub
- [ ] Choose entropy source (not StepID)
- [ ] Implement patches
