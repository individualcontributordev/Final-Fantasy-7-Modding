# v0.1.35 playtest FAIL — music still silent; save OK

**Date:** 2026-08-13
**Status:** fail (music claim)

## APPLIED

movies 0.1.4 + core 0.1.33 (badge 0.1.35) + path 0.1.26 + v0.1.35 + endings. No 0.1.34.

## Result

| Check | Result |
|-------|--------|
| Land #634 LOST2 | PASS |
| Forest music | FAIL (silent) |
| BLACKBGB save page | PASS |
| Black screen | no (not reported) |

## Static verify (same stack)

- LOST2 != pure CSR D2; decompressed differs by exactly 1 byte at IFUB fail E (0x1c to 0x24).
- No LZS cascade corruption; AKAO section identical to CSR D2.
- Script sim a455 + bit4 OFF goes to AKAO2 + MUSIC id=1 + RET.
- Layer 1-byte apply confirmed on image.

## Interpretation

Patch is on the disc and reachable in the sim, but not enough for audible BGM in playtest.

Likely gaps (for next pack, not proven):

1. BLACKBGB disc-2 arms still run MAPJUMP #634 then MUSIC id=3 — MUSIC is after MAPJUMP (never runs on hub). Save arm is the one playtest hit.
2. LOST2 music arms end at MUSIC + RET before ambient channel AKAOs (at 0x63+). If MUSIC alone does not start loop BGM without those AKAOs, field stays silent.
3. GM may not be a455 in live play; then other arms should still hit MUSIC 0/1 on CSR D2 — still silent points to (1)/(2) or audio not MUSIC-gate.

## Do not

- Re-ship COS_BTM2 force / LOSIN2 BITON (0.1.34 class).
- Claim music fixed until playtest PASS.

## Next fix direction

Prefer BLACKBGB: play forest-related MUSIC (or leave volume up) before MAPJUMP #634 on both disc-2 arms; and/or LOST2: after MUSIC, also run ambient AKAO tail without forcing COS MAPJUMP.
