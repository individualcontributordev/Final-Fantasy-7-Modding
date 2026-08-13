# INSTRUCTIONS — Single-disc Gate1 break (v0.1.32)

## Full gates

See docs/single-disc-test-plan.md

## This build

**v0.1.32** — COS_BTM2 break ASK path actually reachable after LOST2 MAPJUMP #526.
v0.1.31 jumped to COS but RET before break (IFSW E landing bug).

## Build

1. Hard-refresh builder (badge **v0.1.32**)
2. CSR + Single-disc only (CSR+ off)
3. APPLIED must include:
   - movies v0.1.4
   - single-disc-on-csr-v0.1.24
   - single-disc-on-csr-v0.1.26
   - single-disc-on-csr-v0.1.31
   - **single-disc-on-csr-v0.1.32**
4. Must NOT list v0.1.27 / 0.1.28 / 0.1.29 / 0.1.30
5. New Disc 1 zip; open the .cue

## Test (Gate 0 + Gate 1 only)

| Check | Expect |
|-------|--------|
| Boot | OK |
| D1 to D2 transition | Completes, no black/glitch |
| Break scene | **COS_BTM2** party/ASK (not straight silent 634) |
| After / on path | Music present |
| Control | Can move/menu |

## Evidence

Paste full APPLIED.txt under this heading after test.

## Evidence (fill in)

- APPLIED:
- PASS/FAIL break + music:
