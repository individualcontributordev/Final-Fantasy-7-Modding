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
FIELD MOVIE/DSKCG engine stubs abandoned for playable builds.

## FMV / media policy (updated)

| Stack | Ask disc | Field Play movie | Extra media on D1 image |
|-------|----------|------------------|-------------------------|
| **Unmodified + no-swap** | Makou delete all DSKCG | **Leave** (wrong FMV for D2/D3 spots OK) | Optional later; Supernova still needs `SNOVA/` or battle fix |
| **CSR + no-swap** | Makou delete all DSKCG (vs CSR baseline) | **Leave** | **Copy manip-critical MOVIE files from D2/D3 onto the D1 image** so FD/list and other CSR manips keep correct streams |
| **CSR + CSR+ scenes + no-swap** | Same | Same | Same copy set + CSR+ scene packs (some already drop FMV-triggering scenes) |
| **Highwind + no-swap** | Makou vs Highwind baseline | Prefer none / already heavily cut | No manip-movie import required |

### CSR manip movies (planned)

- Build **per-base** no-swap pack (or no-swap-on-csr) that can include **ISO layers for selected `MOVIE/*` (and related) files**, not only FIELD scripts.
- Whitelist = movies CSR routing still relies on after disc-change is gone (document list from speedrun/CSR notes + playtest; e.g. any still used for FD / List timing).
- Implementation needs free space on D1 + inject path (not FIELD entry stubs). If a file is too large / no slot, prefer CSR+ scene trim that removes that FMV call instead of forcing a full ending on D1.
- Supernova: still **D3 `SNOVA/`** (~1.1 MB) — good candidate to copy for all bases that reach final battle on D1-only, or battle stub later.

### Why not one pack for all bases

Manip movie set is **CSR-only**. Clean and Highwind packs should not pull unused multi-disc FMVs.
