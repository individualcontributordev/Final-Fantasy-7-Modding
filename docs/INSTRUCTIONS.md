# Task: Disc1 to disc2 break — CSR + Single-disc without CSR+

## What we learned (full stack CSR + CSR+ + SD, no CE)

| Observation | Meaning |
|-------------|---------|
| Unmodified + CSR-only early path OK | CSR base OK; CE likely caused earlier Midgar freezes |
| Slow loads around BCX (CLOUD etc.) | Long CD seeks; hitch then recover — not a hard softlock |
| CSR trims gone after Jenova / spiral | Single-disc replaces Cosmo/LOST/WHITE with CSR Disc 2 fields by design |
| Disc1 to disc2 black + D2 music, no break | LOST2 IFUW to cos_btm2 force is present; CSR+ turns off auto pack single-disc-csr-manip-movies |

Manip-movies seeds D2-related FMVs on Disc 1. With CSR+ checked it is suppressed (unlessAddonIdPrefix csr-plus-scene-). Endings still auto-apply.

## What you do now

### Build C — CSR + Single-disc only (no CSR+)

1. Hard-refresh builder
2. Base: CSR
3. Mods: Single-disc only (CSR+ off, Fanfare off)
4. Build Disc 1
5. APPLIED.txt must include:
   - single-disc-on-csr-v0.1.6 (or current)
   - single-disc-csr-manip-movies (auto)
   - endings parts OK
   - no csr-plus-scene packs
6. Quit DuckStation fully; no CE; no save-state for the transition
7. From in-game save before disc1 to disc2 (or play to it), run the transition

Expect: CSR Disc 2 break / cos_btm2 routing, not only black + music.

### Optional Build D (only if C is OK)

CSR + CSR+ + Single-disc again, same transition — confirm break still fails when movies pack is suppressed.

## Evidence (paste)

```
Build C APPLIED key lines (single-disc + movies present? CSR+ absent?):
Disc1 to disc2: OK BREAK / BLACK+MUSIC / FREEZE / OTHER
Break / cos_btm2 seen?: YES / NO
Playable after?: YES / NO
CE?: NO
notes:
```

## When done

Commit this file with evidence, push, say check.

Commit example: ops: disc1-disc2 break CSR+SD without CSR+ (movies pack on)
