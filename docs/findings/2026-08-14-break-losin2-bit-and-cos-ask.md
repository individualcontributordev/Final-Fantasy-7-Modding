# Disc-break: LOSIN2 must leave bit4 ON; COS must reach ASK

**Date:** 2026-08-14
**Pack:** single-disc-on-csr-v0.1.34

## Multi-disc vs single-disc

After LOSIN2 (D1): GM=0xa455, bank3/0x84#4 **cleared**.
CSR D2 LOST2 with that state: **RET** (no MUSIC, no MAPJUMP 526).
MAPJUMP 526 only if bit4 ON. LOSINN sets BITON 82308404 on multi elsewhere;
LOSIN2 path clears it. Pure D2 LOST2/COS alone never shows break ASK.

## Fix

1. LOSIN2 BITOFF 83308404 -> BITON 82308404
2. COS_BTM2: IFSW E 5->6 (fail to break) + IFUW a455 large else->0
3. LOST2 stays pure CSR D2

Sim: a455+bit4 -> MJ526; COS a455 -> ASK.
