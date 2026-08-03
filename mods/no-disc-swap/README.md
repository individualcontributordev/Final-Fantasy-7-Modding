# No-disc-swap (full-run) — Clean Unmodified D1

Single-disc play on Disc 1 only: no Ask-for-disc, Supernova works.
Builder pack: no-disc-swap-clean-v0.1.0-dev (movie trims). Full-run still open.

Players (later): https://individualcontributor.dev/builder/

## What works (DuckStation, 2026-08-03)

| Piece | Method | Status |
|-------|--------|--------|
| Ask for disc | Makou remove DSKCG on FIELD maps | DS PASS |
| Supernova | D3 SNOVA raw-copy + BATTLE.X LBA remap | DS PASS |
| Combined work bin | Makou then inject once | DS PASS |
| Wrong D2/D3 FMVs | Leave MOVIE vanilla (wrong clip OK) | intentional |
| Console | See docs/INSTRUCTIONS.md smoke | pending |

Engine FIELD MOVIE/DSKCG opcode stubs are abandoned (intro/disc-change softlocks).

## Rebuild recipe (Clean / Unmodified)

### 0. Inputs (gitignored)

- workspace/pristine/FINALFANTASY7_D1.bin
- workspace/pristine/FINALFANTASY7_D3.bin
- Work: workspace/iso-extract/ff7_d1_noswap_work.bin

### 1. Fresh work copy

    cd Final-Fantasy-7-Modding
    git pull --ff-only
    cp -f workspace/pristine/FINALFANTASY7_D1.bin workspace/iso-extract/ff7_d1_noswap_work.bin

### 2. Makou — remove every Ask for disc

Open the work image (not pristine). Delete Ask for disc only; keep Bit clears,
conditions, and map jumps after each ask.

Maps / inventory: docs/findings/2026-08-02-noswap-ask-for-disc-inventory.md

| Map | Field # | Notes |
|-----|---------|--------|
| BLACKBGB | 103 | Priority hub — init S0 Main (4 asks) |
| BLACKBGE | 106 | Completeness |
| BLACKBG3 | 95 | Completeness |

Save FIELD back into the work bin so the ISO is updated.
DS hub smoke before step 3 is recommended.

### 3. SNOVA + BATTLE.X inject (once)

    cp -f workspace/iso-extract/ff7_d1_noswap_work.bin \
          workspace/iso-extract/ff7_d1_noswap_work.pre_snova.bak

    python3 mods/no-disc-swap/scripts/inject_snova_d3_to_d1.py \
      --d1 workspace/iso-extract/ff7_d1_noswap_work.bin \
      --d3 workspace/pristine/FINALFANTASY7_D3.bin \
      --in-place

Must print:

- raw-copy + BATTLE.X LBA patch v3
- verify: BATTLE.X 17 LBA entries remapped
- verify: all SNOVA files match D3

Script refuses double inject. Restore bak or restart from step 1 if needed.

### 4. DuckStation smoke

1. New game → intro FMV → first field
2. One former disc-ask path (no UI; continues)
3. Final battle Supernova (save/cheat) → effect finishes, battle resumes

### 5. Optional console smoke

See root docs/INSTRUCTIONS.md (console section) and docs/07-hardware-burn.md.
New sectors need EDC repair before optical burn; MiSTer/FILE may differ.

### 6. Optional: build builder layer (dev)

    python3 mods/no-disc-swap/scripts/build_clean_d1_layer.py \
      --work workspace/iso-extract/ff7_d1_noswap_work.bin \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin

Writes builder/no-disc-swap-clean-v*/layers/disc1.layer.json from VERSION.
Does not enable the pack in manifest until you decide to ship.

Note: a SNOVA-only layer can be built from ff7_d1_snova_test.bin for inject-only tests; ship layer must come from Ask+Makou combined work bin.


FIELD movie trims (optional polish): patches/field-movie-trims.md + field-movie-inventory-d1.md

## FMV policy (Clean)

- Do not stub MOVIE; do not import full D2/D3 movies for Clean.
- Wrong FMV may play at multi-disc moments; often not full length while the
  field wait still spans the original duration → List/manip timers that
  key off that wait still line up. See
  docs/findings/2026-08-03-noswap-fmv-wait-vs-stream.md.
- CSR base may still want a small manip-critical movie file whitelist later;
  CSR+ / Highwind rely on trims (no movie copy). Prefer try without copies first.

## Layout

    mods/no-disc-swap/
      VERSION
      README.md
      CHANGELOG.md
      patches/README.md
      scripts/
        inject_snova_d3_to_d1.py
        build_clean_d1_layer.py
        stub_field_movie_dskcg.py   # RE only — not for playable bins

## Ship gate (do not skip)

Full single-disc run expectation on Clean D1, then console confidence, then
enabled: true on a versioned pack. Hub-only or SNOVA-only is not shippable alone.
