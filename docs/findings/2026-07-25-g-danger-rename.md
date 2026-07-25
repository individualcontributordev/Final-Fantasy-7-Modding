# g_danger rename via lhu xref

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [encounter-check](2026-07-25-encounter-check.md)

## Summary

Renamed Danger operand to `g_danger` from the `lhu` at `0x800ABC1C`. Direct Go To `0x8007173C` fails (RAM outside FIELD.BIN).

## Discovery

Listing after rename:

```
800abc1c 3c 17 84 94     lhu        a0,offset g_danger(a0)
```

## Follow-ups

- [ ] Fix `encounter_check` true function start (`unaff_s1`)
