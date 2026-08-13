# Gate1: COS_BTM2 IFSW E landed on RET (v0.1.32)

**Date:** 2026-08-14
**Status:** shipped v0.1.32

## APPLIED (playtest fail on 0.1.31)

Base CSR v0.14.1, CSR+ off. Mods: movies 0.1.4, SD 0.1.24 (badge 0.1.31),
break 0.1.31, path 0.1.26, endings parts 1-7. No 0.1.27-30.

## Analysis

Local rebuild of that stack: LOST2 init with GM=0xa455 -> MAPJUMP #526 (OK).
COS_BTM2 directr/0 with a455 still hit **RET @0x72** before break IFUW @0x73.

FFRTT IF fail target = address of E byte + E:

- IFSW @0x66, size 8, E@0x6d, E=5 -> fail 0x72 = RET
- fail-after formula would hit 0x73; game uses E-byte-relative

v0.1.31 only set C from >= to ==; both OK and FAIL still RET for a455 path
through music AKAOs into that IFSW.

## Fix

| Patch | Effect |
|-------|--------|
| IFSW E 5->6 | fail -> 0x73 break IFUW |
| IFSW C ==0x0202 | a455 does not take SETBYTE/RET as "match" |
| IFUW a455 large else ->0 | fall through break AKAO/REQ/ASK |

Sim a455 reaches ASK. Timeout still sets GM 0xa502 and MAPJUMP 634.
