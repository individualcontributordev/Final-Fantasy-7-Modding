# FUN_800a16cc is field main loop; clears Danger after battle

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [danger-clear-site](2026-07-25-danger-clear-site.md)

## Summary

`FUN_800a16cc` @ **`0x800A16CC`** owns the `g_danger = 0` at `0x800A1C70`. It is a large **field main / mode loop**, not a dedicated cleanup-only function. Prefer label **`field_main_loop`**.

## Discovery

Decompiler (excerpt):

```
if ((DAT_800965ec == 2) && (DAT_8007ebc8 == 1)) {
  DAT_8007ebc8 = 0;
  g_step_fraction = 0;
  g_danger = 0;
  DAT_8009abf5 = 0;
}
```

Mode `2` + battle flag → clear Danger / step fraction (return-from-battle). Function also inits GPU-ish state, `while(true)`, map switches via `DAT_8009abf5`, calls `FUN_800aa870`, `FUN_800a2d5c`, `FUN_800a2314`.

## Implications

- Vanilla Danger clear on battle return: **confirmed** here.
- Field-enter Danger = 0 still **missing** — look at map-load helpers (`FUN_800aa870`, `FUN_800a2d5c`, …).

## Follow-ups

- [x] Rename `FUN_800a16cc` → `field_main_loop`
- [ ] Identify field map load / enter hook for Danger = 0
