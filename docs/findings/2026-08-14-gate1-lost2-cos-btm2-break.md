# Gate1: LOST2 to COS_BTM2 break (v0.1.31)

**Date:** 2026-08-14
**Status:** shipped v0.1.31

## Playtest

v0.1.30 (= v0.1.9 field bytes): transition completes, no break, no music on #634.

## Root cause

1. LOSIN2 sets GM=0xa455, clears bank3/0x84 bit4.
2. LOST2 init: that state hits RET (no MUSIC, no MAPJUMP #526).
3. COS_BTM2 IFSW GM>=0x0202 RETs before break ASK when GM is a455
   (why pure force of MAPJUMP alone blacked the break in v0.1.6-0.1.7).

## Fix

| Field | Patch |
|-------|--------|
| LOST2 | Music-branch IFUW !=a455 else 0x12 to 0x13 so fail lands on MAPJUMP path |
| COS_BTM2 | IFSW before break RET: compare >= to == for value 0x0202 |
| BLACKBGB | Ask-stripped only (v0.1.9) |

COS timeout sets GM=0xa502 then MAPJUMP #634 (no infinite a455 loop).

## Stack cleanup

Disabled auto: 0.1.27-0.1.30. Enabled: 0.1.24 + 0.1.26 + 0.1.31.
