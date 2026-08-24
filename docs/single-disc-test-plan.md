# Single-disc test plan (lock gates, no regression churn)

> **Stale snapshot (verified 2026-08-24):** References pack versions
> `single-disc-on-csr-v0.1.24` through `v0.1.33` and CSR `v0.14.1`.
> Single-disc is now at `v0.2.12` (`mods/single-disc/VERSION`) and gates
> below may already be locked/resolved. Treat this as a historical gating
> methodology example, not a current status board.

**Goal:** Prove each fixed surface once, then only open the *next* unfixed gate.
Do not re-touch a locked area unless a later fix fails its own regression row.

**Stack (default playtest):** CSR only + Single-disc (CSR+ **off**)  
**APPLIED should include:** movies `v0.1.4`, core `single-disc-on-csr-v0.1.24`,
auto-deltas through the current badge (e.g. `v0.1.26`…`v0.1.30`).

Player UI is still **one** "Single-disc" checkbox; numbered packs below are
internal layers (see [Pack layering](#pack-layering)).

## Rules

1. **One build per gate wave.** Rebuild only if APPLIED/badge is wrong.
2. **Fail-closed.** Gate N fails → stop; fix only that gate; re-run 0…N.
3. **Save-state after every PASS** (`G0-boot`, `G1-pass`, …).
4. **Do not "improve" locked fields** after that gate is PASS (list per gate).
5. **Report:** `PASS`/`FAIL` + one line + APPLIED snippet on FAIL.

## Gate 0 — Build sanity

| Check | PASS |
|--------|------|
| Boot Disc 1 `.cue` | Title / load works |
| No 80:00 seek failures | Clean boot |
| APPLIED | movies + single-disc core + current deltas |

## Gate 1 — Disc 1→2 transition (priority until green)

**Lock after PASS:** `LOSIN2`, `BLACKBGB`, `LOST2`, `COS_BTM2`  
Reference baseline: **v0.1.33** (pure CSR D1/D2 break fields; no LOST2/COS forces).
Prior spiral: 0.1.27–0.1.32 removed. Target fix: **v0.1.31** (LOST2 a455 to #526 + COS open for a455; Ask BLACKBGB).
Disabled dead ends: 0.1.27-0.1.30. After PASS lock LOST2/COS_BTM2/BLACKBGB/LOSIN2.

| # | Spot | PASS | Known FAIL |
|---|------|------|------------|
| 1a | Hub / disc-change | Continues, no freeze | Hang / insert-disc |
| 1b | Graphics | Stable art | Garbage on transition |
| 1c | Break / open | Same quality as v0.1.9 | Black + random music |
| 1d | Music | Present after settle | Silent #634 only |
| 1e | Control | Walk / menu | Softlock |

## Gate 2 — Cosmo / early D2 smoke

After G1 PASS: LOST2 walkable, nearby Cosmo loads OK. No LOST2/BLACKBGB edits.

## Gate 3 — Highwind path FMVs

**Lock after PASS:** path engine ids, `MOVIE_ID` LBA, FSHIP/MD8 scripts.

| Order | Field | PASS |
|-------|--------|------|
| 3a | FSHIP_24 (#71) | CSR D2 **trim** |
| 3b | FSHIP_12 (#67) | Deck → MD8_5 |
| 3c | MD8_5 (#731) | Full **PARASHOT**; field OK after |
| 3d | MD8_52 (if hit) | **NRCRL** / Cloud position |

## Gate 4 — BLIN66_6 (#255)

CSR D2 trim (same class as #71).

## Gate 5 — Waterfall / movie seek

LOSLAKE (or usual waterfall save): seek + audio OK; no 80-min fail.

## Gate 6 — Hojo / post-Hojo

Only after G1 + G3 locked. Touch **only** Hojo path (`CANON_2`, post-Hojo hub),
not break fields or PARASHOT path.

| # | Spot | PASS |
|---|------|------|
| 6a | Pre-Hojo | Loads clean |
| 6b | Hojo / CANON_2 | Audio + transition |
| 6c | After Hojo | Hub → next field (e.g. LAS0_1 path) |

## Gate 7 — Endings (defer)

Separate endings packs; do not mix into break debugging.

## Workflow

```
G0 FAIL → builder/APPLIED/boot only
G1 FAIL → break fields only
G1 PASS → LOCK break; open G2–G3
G3 FAIL → path FMV / MOVIE_ID only
G3 PASS → LOCK path FMVs
G6 FAIL → Hojo/CANON_2 only
```

**Never** one pack that mixes break force + path FMV remap + Hojo.

## Reply checklist

```
Build: badge ____  APPLIED current? Y/N
G0 boot:     PASS/FAIL
G1 break:    1a__ 1b__ 1c__ 1d__ 1e__   overall PASS/FAIL
G2 cosmo:    PASS/FAIL/skip
G3 path:     71__  FSHIP_12__  PARASHOT731__  (MD8_52__)
G4 #255:     PASS/FAIL/skip
G5 waterfall:PASS/FAIL/skip
G6 Hojo:     PASS/FAIL/skip
New (only if prior PASS): _______________
```

## Pack layering

**Player-facing:** one mod — "Single-disc". Extra `v0.1.2x` packs are
`uiHidden` and auto-apply with the core checkbox.

**Why deltas exist:** GitHub Pages ~100MB/file; core `v0.1.24` is already large.
Small auto layers ship one fix without re-uploading the whole disc diff. Also
lets a bad experiment (e.g. 0.1.27–0.1.29) be undone by a later delta (0.1.30)
without rewriting history mid-playtest.

**Not required long-term.** After Gate 1 (and ideally G3) PASS, **squash**
enabled auto-deltas into a new core (e.g. `v0.1.31` full layer vs CSR+movies),
disable old auto packs, keep one visible Single-disc id. Keep **separate**
families only when they are different products:

| Family | Keep separate? |
|--------|----------------|
| `single-disc-on-csr-v*` | One cumulative core (squash deltas when stable) |
| `single-disc-csr-manip-movies-v*` | Yes — CSR speedrun movies; optional vs CSR+ |
| `single-disc-endings-v* part1–7` | Yes — size split; own feature |

Do **not** merge movies/endings into the field core unless size and apply-order
rules are redesigned on purpose.
