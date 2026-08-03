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
| **Unmodified + no-swap** | Makou delete all DSKCG | **Leave** (wrong FMV for D2/D3 spots OK) | No manip-movie import; Supernova still needs `SNOVA/` or battle fix if final battle is reached |
| **CSR + no-swap** (base only) | Makou delete all DSKCG (vs CSR baseline) | **Leave** | **Copy manip-critical MOVIE files from D2/D3 onto D1** so CSR manips (FD/List, etc.) keep correct streams |
| **CSR + CSR+ scene packs + no-swap** | Same Asks | Scenes that would play those FMVs are **already trimmed** by CSR+ | **No movie copy for CSR+** — wrong PMVIE/set-movie values are irrelevant because the packs do not play those FMVs |
| **Highwind + no-swap** | Makou vs Highwind baseline | Trims remove the play paths | **No movie copy** — wrong set-movie values not a concern |

### CSR base manip movies (CSR-only, planned)

- Only when no-swap is aimed at **CSR base** routing that still runs the FMV.
- Whitelist from speedrun/CSR notes + playtest; ISO inject of selected `MOVIE/*` onto D1 (not FIELD MOVIE stubs).
- If a movie will not fit: prefer a scene trim that drops the play, or accept skip — do not stuff full endings onto D1 without need.

### CSR+ packs and Highwind — no movie import

- **CSR+ scene packs:** cutscene/FMV paths are removed or skipped by design. Do **not** copy D2/D3 movies for CSR+; leftover set-movie ids are harmless if nothing plays them.
- **Highwind:** same — aggressive trims; no manip-movie import; wrong set-movie not a concern.
- **Supernova (`SNOVA/`):** still separate if the final battle is reachable on that stack; not solved by CSR+ trims alone.

### Why not one pack for all bases

- Clean: Asks only (+ optional wrong FMV).
- CSR base: Asks + **optional manip movie files**.
- Highwind / CSR+ context: Asks only; **no** movie payload.

