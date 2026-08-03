# Finding: D1 field PMVIE scan for no-disc-swap crawl risk

**Date:** 2026-08-03
**Status:** automated inventory; Makou verify required

## Context

Operator: missing movie can slow field to a crawl; trimming Set+Play fixes.
Same approach on final descent BG movie. Asked for other D1 instances.

## Method

LZS-decompress pristine D1 FIELD/*.DAT, parse script section, find 0xF8 then 0xF9
within 48 bytes. Map movie id via sorted MOVIE/ names on D1.

## Output

mods/no-disc-swap/patches/field-movie-inventory-d1.md

- Tier 1: id → non-stream D1 file (BIN/LZS/DAT/STAFF/NULL…) — crawl candidates
- Tier 2: OOB ids — many false positives
- Tier 3: valid streams — wrong FMV only

LOSLAKE3 id 58 → OPENING.BIN in Tier 1 (matches known bug).

## Action

Operator continues Makou trims using Tier 1 + Find All; rebuild layer when done.

## Follow-up

D2/D3 exclusive movies used by field scripts (trim candidates on D1):
mods/no-disc-swap/patches/field-movie-d2d3-missing-on-d1.md
