# Task: CSR single-disc — builder-zip workflow + pack rebuild

## How you usually work (primary)

You build a **fresh zip from the site builder**. The zip lives **outside** this repo
workspace. Its name reflects base + mods (whatever the builder emits).

That is the right path for **playtest and console** once packs are published.

    https://individualcontributor.dev/builder/

Example stack (CSR-alone single-disc):

    Base: CSR v0.14.1
    Mods: Single-disc on CSR v0.1.1
          Single-disc CSR manip movies seed v0.1.0
    CSR+ scenes: off

Load pristine NTSC-U Disc 1 .bin into the builder → apply → download zip →
unzip / use the built Disc 1 .bin for DuckStation or burn (EDC repair as usual).

You do **not** need to keep long-lived names under workspace/iso-extract/ for
day-to-day playtest if the builder zip is enough.

---

## When you still need a work .bin (Makou / republish)

Builder layers only ship what is already in git. To **change** field scripts
(BLACKBGB Ask removal) or **add** movies after playtest:

1. Get a Disc 1 .bin that is the current stack (from builder zip extract, or
   verify_builder_config -o — same bytes either way)
2. Makou / inject on that .bin
3. Rebuild layer JSON in this repo vs the correct baseline
4. git push packs
5. **New** builder zip (fresh name from base+mods) for the next playtest

Clean console single-disc zips/bins stay **history only**. CSR packs always
baseline on **CSR**, not Clean.

---

## Baselines (pack rebuild only)

| Baseline | Meaning |
|----------|---------|
| CSR base | pristine + csr-v0.14.1 only |
| Core pack layer | single-disc-on-csr (Ask/crawl trims + SNOVA; BLACKBGB pending Makou) |
| Movie pack layer | single-disc-csr-manip-movies (id-slot seed files on top of CSR+core) |

    Core pack  = (CSR + core edits)  minus  CSR base
    Movie pack = (CSR + core + movies)  minus  (CSR + core)

Never: Clean console bin minus Clean, or Clean bin as CSR starting point.

---

## Path A — playtest only (no pack content change)

1. git pull (so Pages/CDN has latest packs) or wait for deploy after a push
2. Builder: pristine D1 + CSR + single-disc-on-csr + manip-movies seed; no CSR+
3. Download zip (outside workspace; name = builder default)
4. Play / burn from that zip
5. Notes: crawls, Ask, bad FMV name + map → paste or whitelist later

No workspace bin required.

---

## Path B — BLACKBGB Makou then republish core (+ refresh movies)

### B1. Start image = current published stack without needing old noswap names

Option 1 (matches your habit): builder zip with

    CSR + single-disc-on-csr only   (movies optional; for Makou FIELD-only, core-only is enough)

Extract Disc 1 .bin from the zip. Put it anywhere you like (Desktop, etc.).

Option 2 (repo script):

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base csr-v0.14.1 \
      --addon single-disc-on-csr-v0.1.1 \
      --csr-root /Users/david.morton/Final-Fantasy-7-CSR \
      -o /path/to/ff7_d1_csr_single_disc_core_for_makou.bin

### B2. Makou

Open that Disc 1 .bin.

1. blackbgb — remove Ask for disc
2. Keep CSR jumps / bits (do not paste Clean BLACKBGB)
3. Save FIELD into the same .bin

### B3. CSR base bin (for layer diff only)

Needed once to diff. Can live under workspace (gitignored) or any path:

    python3 scripts/apply_layer.py workspace/pristine/FINALFANTASY7_D1.bin \
      /Users/david.morton/Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json \
      -o workspace/iso-extract/ff7_d1_csr_base.bin

### B4. Rebuild core pack

WORK = your Makoued .bin from B2  
BASE = ff7_d1_csr_base.bin

    python3 -c "import json,sys; from pathlib import Path; sys.path.insert(0,"scripts"); from bin_diff_to_layer import build_layer; base=Path("workspace/iso-extract/ff7_d1_csr_base.bin"); work=Path("/path/to/ff7_d1_csr_single_disc_core_for_makou.bin"); out=Path("builder/single-disc-on-csr-v0.1.1/layers/disc1.layer.json"); layer=build_layer(base, work, layer_id="single-disc-on-csr-v0.1.1-disc1", description="Single-disc on CSR after BLACKBGB"); out.write_text(json.dumps(layer, indent=2)+chr(10)); print(layer["stats"])"

Point work= at your real Makoued path.

### B5. Verify core

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base csr-v0.14.1 \
      --addon single-disc-on-csr-v0.1.1 \
      --csr-root /Users/david.morton/Final-Fantasy-7-CSR

### B6. Refresh movie pack (core changed → rebuild movies on new core)

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base csr-v0.14.1 \
      --addon single-disc-on-csr-v0.1.1 \
      --csr-root /Users/david.morton/Final-Fantasy-7-CSR \
      -o workspace/iso-extract/ff7_d1_csr_single_disc_core_applied.bin

    cp -f workspace/iso-extract/ff7_d1_csr_single_disc_core_applied.bin \
          workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin

    python3 mods/single-disc/scripts/inject_movies_by_disc_id.py \
      --d1 workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin \
      --manifest mods/single-disc/patches/csr-manip-movie-seed.txt \
      --in-place

    python3 -c "import json,sys; from pathlib import Path; sys.path.insert(0,"scripts"); from bin_diff_to_layer import build_layer; base=Path("workspace/iso-extract/ff7_d1_csr_single_disc_core_applied.bin"); work=Path("workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin"); out=Path("builder/single-disc-csr-manip-movies-v0.1.0/layers/disc1.layer.json"); layer=build_layer(base, work, layer_id="single-disc-csr-manip-movies-v0.1.0-disc1", description="CSR manip movie seed"); out.write_text(json.dumps(layer, indent=2)+chr(10)); print(layer["stats"])"

### B7. Verify full stack

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base csr-v0.14.1 \
      --addon single-disc-on-csr-v0.1.1 \
      --addon single-disc-csr-manip-movies-v0.1.0 \
      --csr-root /Users/david.morton/Final-Fantasy-7-CSR

### B8. Publish packs

    git pull --ff-only
    git add builder/single-disc-on-csr-v0.1.1 \
            builder/single-disc-csr-manip-movies-v0.1.0 \
            builder/manifest.json docs/ mods/single-disc/
    git commit -m "single-disc: CSR core after BLACKBGB + movie seed refresh"
    git push

Do not commit builder zips or .bin from Desktop/workspace.

### B9. Fresh builder zip again

After Pages updates: new builder zip (new filename from mods) → playtest.
Say **check** so agent verifies packs from git.

---

## Path C — more movies after playtest

1. Note movie file + map (Makou on D2/D3 or whitelist)
2. Add line to mods/single-disc/patches/csr-manip-movie-seed.txt (disc + name)
3. Re-run inject + rebuild movie pack (B6–B8) on current core
4. New builder zip → playtest

---

## Mental model

    Builder zip (outside repo)     =  how you play and iterate builds
    Pack JSON in git (this repo)   =  what the builder applies
    Makou on a .bin                =  only when pack content must change
    Next playtest                  =  always a **new** builder zip after push

Clean console zip/bin: proof only. CSR packs: CSR baseline always.

---

## Evidence (for check)

    Path used: builder zip only / Makou then rebuild
    Builder stack selected:
    Zip name (optional):
    BLACKBGB done: yes/no
    verify core / full (if rebuilt):
    push:
    playtest notes:
