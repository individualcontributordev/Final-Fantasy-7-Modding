# DEL1 (#441) restored to CSR (no jump to DEL2 #442)

**Date:** 2026-08-06
**Status:** fixed in single-disc-on-csr-v0.1.1 layer rebuild

## Report

Field 441 (DEL1) should not jump to field 442 (DEL2); that was a CSR trim.

## Measure

| Image | DEL1.DAT | u16 442 (ba 01) MAPJUMP target |
|-------|----------|--------------------------------|
| Pristine D1 | 21700 | present @768 |
| CSR D1 only | 21432 | **absent** |
| single-disc core (old) | 21456 | **present @767** (regressed) |
| single-disc core (new) | 21432 | **absent** (= CSR) |

## Cause

single-disc-on-csr field merge / trims replaced CSR DEL1 with a near-pristine script that still jumps to DEL2.

## Fix

Rebuild core layer with FIELD/DEL1.DAT byte-identical to CSR v0.14.1 D1.
