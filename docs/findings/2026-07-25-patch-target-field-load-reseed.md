# Patch target: field-load reseed

**Date:** 2026-07-25  
**Confidence:** likely  
**Status:** open  
**Related:** [encounter-rng-architecture](2026-07-25-encounter-rng-architecture.md)

## Summary

To make encounters unpredictable, patch **FIELD.BIN** to reseed StepID, Offset, and Formation (and reset Danger) each time a field map loads.

## Context

Current behavior: all RNG state starts at 0 on new game; StepID/Offset persist in save files. Speedrunners exploit the fixed 256-byte table + deterministic counters.

This finding is one **topic-area** mod idea within the broader FF7 PSX modding project — not the project's sole purpose. Goal for this thread: unknown encounters after hard reset; preferably reseed on every field entry.

## Proposed approach (not yet implemented)

### Option A — Field-load reseed (preferred)

Hook field map init in FIELD.BIN:

```
StepID     ← random byte (entropy from PS1 timer or kernel RNG)
Offset     ← random byte
Formation  ← random byte
Danger     ← 0
```

### Option B — Boot-only reseed

Weaker: save files restore predictable StepID/Offset.

### Option C — Replace increment_step_id return

Call kernel PRNG instead of table lookup — maximum chaos, biggest behavior change.

## Entropy sources (PS1)

- Root counter / VBlank (hardware)
- FF7 kernel PRNG (0–255) — precedent: Bone Village field script RNG seeds from IGT

## Ghidra next steps

1. Decompress FIELD.BIN → find `B1 CA EE 6C` table
2. Xref → `increment_step_id`
3. Find field-load init function
4. Code cave + hook

## Follow-ups

- [ ] Extract FIELD.BIN from user's disc
- [ ] Confirm RNG table offset in Ghidra
- [ ] Identify field_map_init hook point
- [ ] Separate pass for WORLD.BIN

## Sources

- Session planning discussion 2026-07-25
- [FF7 speedrun wiki — Field Map RNG](https://ff7speedruns.com/index.php/Field_Map_RNG)
