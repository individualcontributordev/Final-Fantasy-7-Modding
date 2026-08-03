# Task: No-swap — Makou remove all Ask-for-disc (engine stubs abandoned)

## Engine stubs: stop for playable builds

| Approach | Result |
|----------|--------|
| MOVIE entry stubs v1–v4 | Intro softlock |
| DSKCG entry stubs v5–v6 | Intro OK on v5; disc-change **black + silence** |

Do **not** run `stub_field_movie_dskcg.py` for playtest bins anymore.

## Goal this turn

On a **pristine D1 copy** (vanilla FIELD.BIN), use **Makou only** to delete every
**Ask for disc** (DSKCG). Same style as the cleaned blackbgb hub (delete Ask, keep
Bit OFF / jumps / music).

This matches what already worked for blackbgb in script form.

## Work image

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
mkdir -p workspace/iso-extract
cp -f workspace/pristine/FINALFANTASY7_D1.bin workspace/iso-extract/ff7_d1_noswap_work.bin
```

Open **that** bin in Makou (not an engine-stubbed bin).

## Edits (Makou)

1. Find All **Ask for disc** / DSKCG on the whole archive.
2. For **every** hit (known: blackbgb #103, blackbg3 #95, blackbge #106 — plus any others):
   - **Delete** the Ask-for-disc op only
   - Keep Bit OFF, waits, music, MAPJUMP, save UI
   - Do not leave skip-Gotos that jump over Bit OFF
3. Find All again → **0** hits.
4. Save all changed fields back into `ff7_d1_noswap_work.bin`.

## Playtest (DuckStation)

1. **New game** — intro video + first field (must PASS; proves no bad FIELD.BIN patch)
2. **Disc-change hub** (blackbgb paths) — no insert UI; **music + jump** to lost2 / las0_1
3. Optional: any other Ask sites you know

## Evidence

```
Work bin path:
Find All Ask count after edit: 0 / N
Maps edited:
New game: PASS/FAIL
Disc-change blackbgb: PASS/FAIL (music? jump map?)
Notes:
```

Paste one cleaned disc branch if useful. Commit this file with evidence if you want
it in git (no .bin). Say **check**.

## Out of scope this turn

- Engine stub experiments
- FMV cut / Supernova
- Builder pack ship
