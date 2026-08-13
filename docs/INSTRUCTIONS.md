# INSTRUCTIONS — Single-disc Gate1 break (v0.1.31)

## Full gates

See docs/single-disc-test-plan.md

## This build

**v0.1.31** — disc1 to disc2 break scene (COS_BTM2) + open LOST2 path for GM 0xa455.
Auto-deltas 0.1.27 through 0.1.30 are disabled (must not apply).

## Build

1. Hard-refresh builder (badge **v0.1.31**)
2. CSR + Single-disc only (CSR+ off)
3. APPLIED must include:
   - movies v0.1.4
   - single-disc-on-csr-v0.1.24
   - single-disc-on-csr-v0.1.26
   - **single-disc-on-csr-v0.1.31**
4. Must NOT list v0.1.27 / 0.1.28 / 0.1.29 / 0.1.30
5. New Disc 1 zip; open the .cue

## Test (Gate 0 + Gate 1 only)

| Check | Expect |
|-------|--------|
| Boot | OK |
| D1 to D2 transition | Completes, no black/glitch |
| Break scene | **COS_BTM2** (party/ASK), not straight silent field 634 |
| After / on path | Music present |
| Control | Can move/menu |

## Evidence

- APPLIED with **v0.1.31** only (no 27-30)
- PASS/FAIL break + music
