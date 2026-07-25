# g_danger xrefs (all sites)

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Related:** [patch-target-field-load-reseed](2026-07-25-patch-target-field-load-reseed.md), [danger-increment](2026-07-25-danger-increment.md)

## Summary

Only **4** references to `g_danger` in FIELD.BIN:

| Address | Access | Role |
|---------|--------|------|
| `0x800A1C70` | `sh zero` **WRITE** | **Danger = 0** |
| `0x800ABBC0` | `lhu` READ | load before += |
| `0x800ABBD0` | `sh` WRITE | store after += |
| `0x800ABC1C` | `lhu` READ | threshold compare |

## Implications

- Danger `+=` patch site is still `0x800ABB7C`–`0x800ABBD0` inside `encounter_check`.
- Existing clear is **only** at `0x800A1C70` — identify that function (battle end vs field enter vs both).
- If that clear is battle-only, field-enter `Danger = 0` needs a **new** hook.

## Follow-ups

- [ ] Identify function containing `0x800A1C70`
- [ ] Confirm whether field enter already clears Danger (likely not)
