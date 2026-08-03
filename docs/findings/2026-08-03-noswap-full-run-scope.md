# No-swap full-run scope (do not ship incomplete pack)

**Date:** 2026-08-03
**Confidence:** confirmed (layout + prior DS + operator history)
**Policy:** No public builder pack until a full single-disc run is expected to work
on Unmodified D1 (then other bases). Hub-only Ask removal is **not** shippable alone.

## Why hub-only is not enough

| Gap | Failure mode |
|-----|----------------|
| Other field Ask-for-disc (blackbg3, blackbge, …) | Disc prompt / stuck path |
| Multi-disc field movies | Missing STR/MOV hang |
| Battle Supernova (`SNOVA/` D3-only, ~1.1 MB) | Battle freeze (known) |
| Ending / last movies on D3 | Endgame hang |
| DISKINFO / disc id (if re-checked) | Wrong-disc reject |
| Other D2/D3-only MOVIE files hit mid-run | Random freezes |

Shared FIELD maps exist on all discs; **media does not**. No-swap = script gates
+ missing-media policy (skip and/or copy small assets like SNOVA).

## Target product (later)

One **builder pack** (FIELD + whatever engine/data layers needed), full-run safe
on **clean** D1 first; then CSR/Highwind if bytes allow. Not a base bump.

## Done already

- Disc cross-compare; Ask inventory; blackbgb hub branches
- Working edit (Ask removed, Bit OFF kept); DS hub smoke OK
- Path (operator): workspace/iso-extract/ff7_d1_noswap_re.bin

## Open work (order)

1. Inventory all freeze classes on a D1-only image (field Ask, field movie, battle SNOVA, endings)
2. Patch/skip each class on working D1 bin
3. Playtest critical path (disc2 gate, disc3 gate, Supernova, one multi-disc field movie)
4. Diff vs pristine → pack; verify; ship only after playtest PASS

## Local bins (never git commit)

Place under Modding (gitignored):

- workspace/iso-extract/ff7_d1_noswap_re.bin  (current edit)
- workspace/pristine/FINALFANTASY7_D{1,2,3}.bin if missing

Agent can read/diff/edit copies there. Do not force git add on .bin.

## Engine stub outcome (2026-08-03)

- MOVIE (0xF9) entry stubs: softlock intro — **abandoned**
- DSKCG (0x0E) entry stubs: no Ask UI but disc-change **black/silent** — **abandoned** for play

**Playable path:** Makou remove Ask-for-disc (DSKCG) on all maps; pristine FIELD.BIN.
FMV policy + Supernova still open (other hooks / later).
