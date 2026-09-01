# Single-disc (full-run)

Single-disc play: no Ask-for-disc, Supernova on D1, multi-disc field FMV handled
by script trims.

**Current architecture:** single-disc is no longer an add-on applied on top of
a multi-disc base. `csr-plus` and `highwind` are their own collapsed
single-disc **bases** in `builder/manifest.json`, built directly by
the artifact-preserving `build_csrplus_staged.py` and
`build_highwind_staged.py` pipelines. `build_collapsed_bases.py` is retained
for historical investigation, not new releases. See
`docs/CREATE_ADDON_FROM_MAKOU.md` in the CSR repo and
`docs/08-engineer-build-guide.md`'s CLI cookbook. `single-disc-on-csr` and
the CSR manip-movies pack described below are **retired**
(`enabled: false`) — kept only for changelog/history context; do not build
against them.

## Supported bases (builder)

| Base | single-disc? | Notes |
|------|---------------|--------|
| Unmodified / clean | NO | Keep unmodified spirit: other mods OK if they do not change fields or FMVs. |
| `csr` | NO | Still 3-disc; single-disc-on-csr retired, no current single-disc option for CSR alone. |
| `csr-plus` | YES (base itself) | Collapsed CSR+ single-disc base — CSR D1 + rework merges + CSR+ scene trims + table fix + SNOVA inject. |
| `highwind` | YES (base itself) | Collapsed Highwind single-disc base — Highwind D1 + D2/D3 FIELD merge + table fix + SNOVA inject. |

### Retired pack families (historical only)

| Pack | Status |
|------|--------|
| Single-disc (`single-disc-on-csr-v*`) | Retired — replaced by the `csr-plus`/`highwind` collapsed bases. |
| CSR manip movies (`single-disc-csr-manip-movies-v*`) | Retired alongside `single-disc-on-csr`. |
| Clean pack (`single-disc-clean-v0.1.1`) | Retired (`enabled: false`). |

Players: https://individualcontributor.dev/builder/

Builder UI: `csr-plus` and `highwind` are selectable bases (like `clean`/`csr`),
not an add-on checkbox on top of CSR.

**Playtest gates (lock fixes, avoid regressions):** [docs/single-disc-test-plan.md](../../docs/single-disc-test-plan.md).
Delta packs (`v0.1.26`+) are internal auto layers for size/hotfix; squash into one core when a gate wave is green (see that doc).

## What works (DuckStation, 2026-08-03)

| Piece | Method | Status |
|-------|--------|--------|
| Ask for disc | Makou remove DSKCG on FIELD maps | DS PASS |
| Supernova | D3 SNOVA raw-copy + BATTLE.X LBA remap | DS PASS |
| Combined work bin | Makou then inject once | DS PASS |
| Wrong D2/D3 FMVs | Leave MOVIE vanilla (wrong clip OK) | intentional |
| Console | See docs/07-hardware-burn.md smoke checklist | pending |

Engine FIELD MOVIE/DSKCG opcode stubs are abandoned (intro/disc-change softlocks).

## Rebuild recipe (Clean / Unmodified)

### 0. Inputs (gitignored)

- workspace/pristine/FINALFANTASY7_D1.bin
- workspace/pristine/FINALFANTASY7_D3.bin
- Work: workspace/iso-extract/ff7_d1_single_disc_work.bin

### 1. Fresh work copy

    cd Final-Fantasy-7-Modding
    git pull --ff-only
    cp -f workspace/pristine/FINALFANTASY7_D1.bin workspace/iso-extract/ff7_d1_single_disc_work.bin

### 2. Makou — remove every Ask for disc

Open the work image (not pristine). Delete Ask for disc only; keep Bit clears,
conditions, and map jumps after each ask.

Maps / inventory: docs/findings/2026-08-02-single-disc-ask-for-disc-inventory.md

| Map | Field # | Notes |
|-----|---------|--------|
| BLACKBGB | 103 | Priority hub — init S0 Main (4 asks) |
| BLACKBGE | 106 | Completeness |
| BLACKBG3 | 95 | Completeness |

Save FIELD back into the work bin so the ISO is updated.
DS hub smoke before step 3 is recommended.

### 3. SNOVA + BATTLE.X inject (once)

    cp -f workspace/iso-extract/ff7_d1_single_disc_work.bin \
          workspace/iso-extract/ff7_d1_single_disc_work.pre_snova.bak

    python3 mods/single-disc/scripts/inject_snova_d3_to_d1.py \
      --d1 workspace/iso-extract/ff7_d1_single_disc_work.bin \
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

See docs/07-hardware-burn.md. New sectors need EDC repair before optical
burn; MiSTer/FILE may differ.

### 6. Optional: build builder layer (dev)

    python3 mods/single-disc/scripts/build_clean_d1_layer.py \
      --work workspace/iso-extract/ff7_d1_single_disc_work.bin \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin

Writes builder/single-disc-clean-v*/layers/disc1.layer.json from VERSION.
Does not enable the pack in manifest until you decide to ship.

Note: a SNOVA-only layer can be built from ff7_d1_snova_test.bin for inject-only tests; ship layer must come from Ask+Makou combined work bin.


FIELD movie trims (optional polish): patches/field-movie-trims.md + field-movie-inventory-d1.md + field-movie-d2d3-missing-on-d1.md + field-movie-d2d3-after-disc-change.md

## FMV policy (Clean)

CSR base manip movie copies: required second pack with single-disc-on-csr; omit only for CSR+ stacks.
See docs/findings/2026-08-04-single-disc-csr-manip-movies-pack-split.md

- Do not stub MOVIE; do not import full D2/D3 movies for Clean.
- Wrong FMV may play at multi-disc moments; often not full length while the
  field wait still spans the original duration → List/manip timers that
  key off that wait still line up. See
  docs/findings/2026-08-03-single-disc-fmv-wait-vs-stream.md.
- CSR base alone (later): required manip-movie pack when that stack ships; deferred for size.

## Layout

    mods/single-disc/
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
