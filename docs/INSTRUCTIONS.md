# INSTRUCTIONS — Single-disc break scene (badge v0.1.34)

## Build

1. Hard-refresh builder (badge **v0.1.34**)
2. CSR + Single-disc only
3. APPLIED must include:
   - movies v0.1.4
   - single-disc-on-csr-v0.1.33
   - path FMVs v0.1.26
   - **single-disc-on-csr-v0.1.34** (break scene)
4. New Disc 1 zip

## What should happen

D1 to D2: after BLACKBGB hub, LOST2 should MAPJUMP to **COS_BTM2** break/ASK (not drop straight into silent forest only).

## Evidence

Paste APPLIED + PASS/FAIL break scene.

Final Fantasy VII — IndividualContributor

Disc: 1 (layers for this disc only)
Base: CSR v0.14.1
Download: ff7-d1-csr-mov-sd-end.zip
CSR+: off (or no CSR+ layer for this disc)
Mods on this disc:
  - CSR manip movies v0.1.4 (single-disc-csr-manip-movies-v0.1.4)
  - Single-disc v0.1.34 (single-disc-on-csr-v0.1.33)
  - (auto) path FMVs v0.1.26 (single-disc-on-csr-v0.1.26)
  - (auto) disc-break scene v0.1.34 (single-disc-on-csr-v0.1.34)
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
