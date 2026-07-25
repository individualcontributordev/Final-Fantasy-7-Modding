# Field map setup block @ 0x800A1DC8 + FUN_800ba534

**Date:** 2026-07-25  
**Confidence:** likely  
**Related:** [field-main-loop](2026-07-25-field-main-loop.md), [patch-target-field-load-reseed](2026-07-25-patch-target-field-load-reseed.md)

## Summary

When `field_main_loop` takes the map-setup path (**`LAB_800a1dc8`** / `0x800A1DC8`), it resets many field globals, calls **`FUN_800ba534`** (script/module init), then **`FUN_800aa870`** (entities). It does **not** clear `g_danger` — ideal place to add **Danger = 0 on field enter**.

## Discovery

Setup block (excerpt): zeros `DAT_8009ac9a`…, `DAT_80071e38`, etc. → `jal FUN_800ba534` @ `0x800A1E40` → … → `jal FUN_800aa870` @ `0x800A1ED8`.

`FUN_800ba534` @ `0x800BA534`:

- Sets `DAT_8007ebe0 = 1`, stores field pointers (`DAT_8009c6e0`, `DAT_8009c544`, `DAT_8009c6dc`)
- Calls `FUN_800d48c0`, `FUN_800ba7c4`, `FUN_800baf54`, optional `FUN_800c46a4`
- Strong **`field_map_init`** candidate

## Proposed Danger = 0 hooks (pick one)

| Site | Pros |
|------|------|
| Start of `LAB_800a1dc8` (`0x800A1DC8`) | Runs whenever this setup path runs; already zeroing peers |
| Start of `FUN_800ba534` | Single function entry; clean |

## Follow-ups

- [ ] Rename `FUN_800ba534` → `field_map_init`
- [ ] Confirm this path runs on every field enter (incl. first load / door transitions)
- [ ] Implement Danger=0 + replace Danger+= with MAX RNG
