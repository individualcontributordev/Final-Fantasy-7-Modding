# Byte search ran on compressed FIELD.BIN

**Date:** 2026-07-25  
**Confidence:** confirmed

## Observation

`scripts/search_encounter_addrs.py` was run on `workspace/iso-extract/FIELD.BIN` (85435 bytes GZIPPS). All needles returned **0 hits**, including RNG table head `B1 CA EE 6C…`.

## Cause

Compressed payload will not contain plaintext table or RAM pointer bytes. Search must use **`FIELD.BIN.dec`** (264008 bytes).

## Follow-up

Re-run script on `.dec`.
