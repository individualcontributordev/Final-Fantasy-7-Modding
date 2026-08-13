# INSTRUCTIONS — rebuild Disc 1 (Single-disc v0.1.30 break restore)

## Why

v0.1.27–0.1.29 experiments broke the D1→D2 transition (black/glitch, no scene).
This build restores the **v0.1.8/0.1.9** known-good break fields.

## Build

1. Hard-refresh builder (badge **v0.1.30**)
2. CSR + Single-disc only (CSR+ off)
3. APPLIED must include:
   - movies v0.1.4
   - single-disc-on-csr-v0.1.24
   - v0.1.26 … **v0.1.30**
4. New Disc 1 zip; open the .cue

## Test

| Spot | Expect |
|------|--------|
| Disc 1→2 transition | Same as v0.1.9: break works, no black/glitch |
| Music after transition | Present (as before 0.1.27 experiments) |
| PARASHOT #731 / #71 / #255 | Still OK |

## Evidence

- APPLIED.txt with **v0.1.30**
- Pass/fail transition + graphics + music
