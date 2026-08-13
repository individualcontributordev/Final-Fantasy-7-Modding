# INSTRUCTIONS — Single-disc v0.1.33 (CSR reference)

## What changed

Spiral break packs (0.1.27–0.1.32) removed. Single-disc break path follows
CSR Disc 1 + Disc 2 field scripts again (no LOST2/COS_BTM2 force hacks).

## Build

1. Hard-refresh builder (badge **v0.1.33**)
2. CSR + Single-disc only (CSR+ off)
3. APPLIED should include:
   - movies v0.1.4
   - **Single-disc v0.1.33 (single-disc-on-csr-v0.1.33)**
   - path-engine v0.1.26 (internal)
   - CSR field ref v0.1.33 (internal) — pure D2 LOST2+COS_BTM2
   - endings parts 1–7
4. Must NOT list 0.1.27–0.1.32 spiral packs
5. New Disc 1 zip

## Test (Gate 0 + Gate 1)

Compare mentally to multi-disc CSR D1→D2:

| Check | Expect |
|-------|--------|
| Boot | OK |
| D1→2 transition | Completes (no insert-disc hang) |
| After transition | Cosmo/lost forest playable |
| Music | Note pass/fail (honest CSR parity) |
| Graphics | No glitch from force patches |

## Evidence

Paste full APPLIED.txt here.
