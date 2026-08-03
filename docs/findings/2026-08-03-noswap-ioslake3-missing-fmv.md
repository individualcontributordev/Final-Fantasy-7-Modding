# Finding: ioslake3 missing FMV (not freeze) on Clean no-disc-swap

**Date:** 2026-08-03
**Status:** observed on Clean + no-disc-swap (console or DS playtest)
**Map:** ioslake3 — group S0 Main (operator report)

## Symptom

- Not a hard freeze
- Bugenhagen stays on-field (animated / idle)
- An FMV is supposed to play and does not

## Script shape (operator)

S0 Main roughly:

1. Set next movie: No57 (D1) / ioslake1 (D2) / No57 (D3)
2. Play movie
3. Another Set next movie
4. Play movie
5. Jump (progress)

## Diagnosis

Clean no-disc-swap **leaves MOVIE vanilla**. Multi-disc set-movie tables often point at
streams that are wrong or empty on D1-only. Result can be:

- no visible FMV
- character left in place during the wait
- script still eventually continues (or feels stuck if wait is long)

This is **media/presentation**, not Ask-for-disc and not Supernova.

## Policy call (Clean)

| Goal | Action |
|------|--------|
| Full-run progress only | **Leave** movie ops if the Jump still fires after the wait |
| Avoid long empty stares | Makou: remove **Play movie** (and redundant Set next movie); **keep Jump** + flags |
| Correct video on D1 | Copy the needed MOVIE file(s) onto D1 (large; not default for Clean) |

Do **not** engine-stub MOVIE (0xF9) — breaks intro.

## Next

1. Confirm whether the field eventually advances without input after N seconds
2. If yes and only cosmetics: optional trim for polish, not a blocker
3. If never advances: must trim Play movie ops (treat like soft hang)
4. Push Makou script dump under mods/no-disc-swap/patches/field/ for exact line list

## Related

- 2026-08-03-noswap-fmv-wait-vs-stream.md
- 2026-08-03-noswap-full-run-scope.md FMV policy
