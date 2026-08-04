# Task: CSR single-disc — correct baselines + playtest / publish

## Do not confuse these images

| Image | Baseline | What it is | Use for CSR pack? |
|-------|----------|------------|-------------------|
| Clean single-disc work (old noswap_work / clean console burn) | **Clean / Unmodified D1** | Ask + crawl movie trims + SNOVA validated on console | **NO** — wrong base |
| ff7_d1_csr_base.bin | Pristine + **csr-v0.14.1** only | CSR routing, no single-disc | Diff **against** this for core pack |
| CSR single-disc core work | **CSR base** + field Ask/crawl trims + SNOVA | Core single-disc content | YES — pack input |
| CSR + movie seed work | Core applied + 4 movies by id | CSR-alone playtest | YES — movie pack input |

**Clean console bin is a recipe source for which FIELD maps to trim, not a binary to layer onto CSR.**

BLACKBGB on Clean must not be pasted over CSR (CSR already edited that hub).

---

## Correct product model

### Pack 1 — single-disc-on-csr (core)

    Start:  CSR base (not Clean)
    Edit:   Ask removals + crawl Set/Play trims on maps CSR did not own
            + Makou BLACKBGB on **CSR** script
            + SNOVA/BATTLE.X
    Layer:  (that work bin) minus (CSR base) 
    Id:     single-disc-on-csr-v0.1.1

### Pack 2 — single-disc-csr-manip-movies (optional for CSR-alone)

    Start:  CSR base + core pack applied
    Edit:   overwrite D1 movie **ids** with seed list (LASTFLOR, …)
    Layer:  (movies work) minus (CSR + core applied)
    Id:     single-disc-csr-manip-movies-v0.1.0

### Playtest stack

    Base: csr-v0.14.1
    + single-disc-on-csr
    + single-disc-csr-manip-movies   (CSR-alone only; omit if using CSR+)
    CSR+ scenes: off for this stack

You do **not** take Clean console .bin, drop movies in, and call that the CSR mod.

---

## What is already done in repo

| Step | Status |
|------|--------|
| Core pack vs CSR (field trims from Clean **recipe**, not Clean bin; BLACKBGB still CSR) | Published single-disc-on-csr-v0.1.1 |
| Movie seed pack (4 files by id) | Published single-disc-csr-manip-movies-v0.1.0 |
| Clean console validation | Informs which trims matter; Unmodified pack retired |
| BLACKBGB Ask on CSR core | **Your Makou next** |
| Rebuild core + movies after BLACKBGB | After Makou |
| Expand movie list after playtest | Later |

---

## Paths (gitignored — never commit)

| Path | Role |
|------|------|
| workspace/pristine/FINALFANTASY7_D{1,2,3}.bin | Retail |
| workspace/iso-extract/ff7_d1_csr_base.bin | CSR only |
| workspace/iso-extract/ff7_d1_csr_single_disc_core_work.bin | CSR + core single-disc edits |
| workspace/iso-extract/ff7_d1_csr_single_disc_core_applied.bin | Pristine+CSR+core layers |
| workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin | Core applied + movies |
| Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json | CSR layer |

Ignore Clean-named bins (ff7_d1_noswap_work.bin, clean_noswap built, etc.) for CSR packaging.

---

## Phase A — CSR baseline

    cd /path/to/Final-Fantasy-7-Modding
    git pull --ff-only

    python3 scripts/apply_layer.py workspace/pristine/FINALFANTASY7_D1.bin \
      /Users/david.morton/Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json \
      -o workspace/iso-extract/ff7_d1_csr_base.bin

---

## Phase B — core work on CSR (not Clean)

### B1. Start core work from CSR base

If you do not already have a CSR-based core work bin from the agent build:

    cp -f workspace/iso-extract/ff7_d1_csr_base.bin \
          workspace/iso-extract/ff7_d1_csr_single_disc_core_work.bin

Then you need the core field trims + SNOVA on this file (agent already produced a CSR-based work as
ff7_d1_csr_noswap_work.bin earlier — **that** one is CSR-based despite the old name). Prefer:

    # Only if this file is the CSR+trims+SNOVA build (not Clean):
    cp -f workspace/iso-extract/ff7_d1_csr_noswap_work.bin \
          workspace/iso-extract/ff7_d1_csr_single_disc_core_work.bin

**Never** cp Clean console noswap_work.bin into csr_single_disc_core_work.

### B2. Makou BLACKBGB on CSR core work

Open: ff7_d1_csr_single_disc_core_work.bin

1. blackbgb — remove Ask for disc only
2. Keep CSR jumps / bits
3. Save into same bin

### B3. SNOVA if this core work lacks it

    python3 mods/single-disc/scripts/inject_snova_d3_to_d1.py \
      --d1 workspace/iso-extract/ff7_d1_csr_single_disc_core_work.bin \
      --d3 workspace/pristine/FINALFANTASY7_D3.bin \
      --in-place

Skip if already injected on this file.

---

## Phase C — rebuild + verify core pack

Layer = core work minus CSR base:

    python3 -c "import json,sys; from pathlib import Path; sys.path.insert(0,"scripts"); from bin_diff_to_layer import build_layer; base=Path("workspace/iso-extract/ff7_d1_csr_base.bin"); work=Path("workspace/iso-extract/ff7_d1_csr_single_disc_core_work.bin"); out=Path("builder/single-disc-on-csr-v0.1.1/layers/disc1.layer.json"); layer=build_layer(base, work, layer_id="single-disc-on-csr-v0.1.1-disc1", description="Single-disc on CSR after BLACKBGB"); out.write_text(json.dumps(layer, indent=2)+chr(10)); print(layer["stats"])"

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base csr-v0.14.1 \
      --addon single-disc-on-csr-v0.1.1 \
      --csr-root /Users/david.morton/Final-Fantasy-7-CSR

Must PASS.

---

## Phase D — movies on CSR+core (not on Clean)

    python3 -c "import json,sys; from pathlib import Path; sys.path.insert(0,"scripts"); from apply_layer import apply_layer; pr=Path("workspace/pristine/FINALFANTASY7_D1.bin").read_bytes(); csr=json.loads(Path("/Users/david.morton/Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json").read_text()); core=json.loads(Path("builder/single-disc-on-csr-v0.1.1/layers/disc1.layer.json").read_text()); img=bytearray(pr); apply_layer(img,csr); apply_layer(img,core); Path("workspace/iso-extract/ff7_d1_csr_single_disc_core_applied.bin").write_bytes(bytes(img)); print(len(img))"

    cp -f workspace/iso-extract/ff7_d1_csr_single_disc_core_applied.bin \
          workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin

    python3 mods/single-disc/scripts/inject_movies_by_disc_id.py \
      --d1 workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin \
      --manifest mods/single-disc/patches/csr-manip-movie-seed.txt \
      --in-place

Rebuild movie pack (movies work minus core applied):

    python3 -c "import json,sys; from pathlib import Path; sys.path.insert(0,"scripts"); from bin_diff_to_layer import build_layer; base=Path("workspace/iso-extract/ff7_d1_csr_single_disc_core_applied.bin"); work=Path("workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin"); out=Path("builder/single-disc-csr-manip-movies-v0.1.0/layers/disc1.layer.json"); layer=build_layer(base, work, layer_id="single-disc-csr-manip-movies-v0.1.0-disc1", description="CSR manip movie seed"); out.write_text(json.dumps(layer, indent=2)+chr(10)); print(layer["stats"])"

---

## Phase E — verify full stack + optional built bin

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base csr-v0.14.1 \
      --addon single-disc-on-csr-v0.1.1 \
      --addon single-disc-csr-manip-movies-v0.1.0 \
      --csr-root /Users/david.morton/Final-Fantasy-7-CSR \
      -o workspace/iso-extract/ff7_d1_csr_single_disc_full_built.bin

Must PASS.

---

## Phase F — playtest

DuckStation: ff7_d1_csr_single_disc_full_built.bin (Disc 1 only).

Or builder after push: CSR + both single-disc packs, no CSR+.

Checks: boot, blackbgb no Ask, Supernova, seed FMVs, note other crawls for later movies.

---

## Phase G — publish

    git add builder/single-disc-on-csr-v0.1.1 \
            builder/single-disc-csr-manip-movies-v0.1.0 \
            builder/manifest.json docs/ mods/single-disc/
    git commit -m "single-disc: CSR core after BLACKBGB + movie seed refresh"
    git push

No .bin files.

Say **check** — agent re-verifies packs from repo.

---

## Minimal mental model

    Clean console bin  →  proof that trims/SNOVA work (history only)
    CSR base           →  required baseline for CSR packs
    CSR + core edits   →  single-disc-on-csr pack
    CSR + core + movies →  single-disc-csr-manip-movies pack + playtest image

---

## Evidence

    Used CSR base (not Clean bin): yes/no
    BLACKBGB Makou on CSR core work:
    verify core:
    verify full:
    playtest:
    push:
