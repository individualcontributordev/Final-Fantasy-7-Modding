# DuckStation accurate settings

**Date:** 2026-07-25  
**Confidence:** confirmed  
**Status:** promoted → `docs/03-environment-setup.md`  
**Related:** [encounter-rng-architecture](2026-07-25-encounter-rng-architecture.md)

## Summary

Use **Safe Mode** in DuckStation for hardware-like behavior when testing encounter RAM and patches.

## Discovery

### One-click: Safe Mode

**Settings → Main → Safe Mode** (`DisableAllEnhancements`)

Forces via `Settings::ApplySettingRestrictions()`:

- GPU 1x, PGXP off, nearest filtering
- CPU overclock off
- CD read/seek speedup = 1x
- Fast boot off
- Runahead, rewind off
- Cheats-compatible baseline

### Also verify manually

| Setting | Value |
|---------|-------|
| Region | Match disc (US/EU/JP) |
| Cheats | Off during patch tests |
| CPU execution mode | Recompiler (default); Interpreter only for JIT debugging |
| Fast forward | Don't use while testing timing |

### Memory watch addresses (US)

`0x8007173C` Danger · `0x8009C540` StepID · `0x8009AD2C` Offset · `0x80071C20` Formation

### Not required for encounter testing

- Software GPU renderer (accurate visuals, irrelevant to RNG RAM)
- Accurate blending / upscaling

### Emulator ≠ hardware

Safe Mode is sufficient for patch dev; validate final builds on real PS1 if possible.

## Sources

- DuckStation `src/core/settings.cpp` — `ApplySettingRestrictions()`
- DuckStation `src/core/system.cpp` — `WarnAboutUnsafeSettings()`
