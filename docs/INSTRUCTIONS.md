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


Final Fantasy VII — IndividualContributor

Disc: 1 (layers for this disc only)
Base: CSR v0.14.1
Download: ff7-d1-csr-mov-sd-end.zip
CSR+: off (or no CSR+ layer for this disc)
Mods on this disc:
  - CSR manip movies v0.1.4 (single-disc-csr-manip-movies-v0.1.4)
  - Single-disc v0.1.31 (single-disc-on-csr-v0.1.24)
  - Single-disc break (internal) v0.1.31 (single-disc-on-csr-v0.1.31)
  - Single-disc path-engine (internal) v0.1.26 (single-disc-on-csr-v0.1.26)
  - Single-disc ending credits v0.1.0 (single-disc-endings-v0.1.0-part1)
  - Single-disc ending credits (part 2) v0.1.0 (single-disc-endings-v0.1.0-part2)
  - Single-disc ending credits (part 3) v0.1.0 (single-disc-endings-v0.1.0-part3)
  - Single-disc ending credits (part 4) v0.1.0 (single-disc-endings-v0.1.0-part4)
  - Single-disc ending credits (part 5) v0.1.0 (single-disc-endings-v0.1.0-part5)
  - Single-disc ending credits (part 6) v0.1.0 (single-disc-endings-v0.1.0-part6)
  - Single-disc ending credits (part 7) v0.1.0 (single-disc-endings-v0.1.0-part7)
EDC/ECC sectors repaired: 80468

Play:
- Keep the .bin and .cue in the same folder.
- Open the .cue in DuckStation (or your emulator).
- Real PS2 (MechaPwn): burn from the .cue as MODE2/2352 DAO (see Modding docs/07-hardware-burn.md).
- Builder regenerates Mode2 Form1 EDC/ECC on patched sectors after applying layers.

https://individualcontributor.dev/builder/
