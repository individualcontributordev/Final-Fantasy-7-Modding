# Ghidra scalar search found no StepID immediates

**Date:** 2026-07-25  
**Confidence:** confirmed (user report)

## Observation

After labeling RNG table at `0x80040638`, **Search → For Scalars** for `0x9c540`, `0xc540`, and decimal equivalents returned **no hits**.

## Implication

Encounter RAM may be reached via a base pointer / struct offset, not bare `lui`/`lbu` immediates Ghidra indexes as scalars — or the US wiki addresses differ for this build. Next: raw byte search in `FIELD.BIN.dec` (`scripts/search_encounter_addrs.py`) and/or DuckStation PC watch when StepID changes.
