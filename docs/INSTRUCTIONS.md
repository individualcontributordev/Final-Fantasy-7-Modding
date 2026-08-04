# Task: CSR single-disc — full build / Makou / verify / playtest / publish

End-to-end for CSR alone (no CSR+ scenes):

1. Core pack: Ask trims + field movie crawl trims + SNOVA (BLACKBGB Makou still open)
2. Movie seed pack: 4 multi-disc movies by PMVIE id onto D1
3. After BLACKBGB: rebuild core, then rebuild movies, push, playtest from builder

## Paths (gitignored bins — do not commit)

| Path | Role |
|------|------|
| workspace/pristine/FINALFANTASY7_D1.bin | Retail D1 |
| workspace/pristine/FINALFANTASY7_D2.bin | Retail D2 (movie source) |
| workspace/pristine/FINALFANTASY7_D3.bin | Retail D3 (movie + SNOVA source) |
| workspace/iso-extract/ff7_d1_csr_base.bin | CSR base only (layer apply) |
| workspace/iso-extract/ff7_d1_csr_single_disc_core_work.bin | Core work (Makou + SNOVA) |
| workspace/iso-extract/ff7_d1_csr_single_disc_core_applied.bin | Pristine+CSR+core layer apply |
| workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin | Core + movie seed |
| Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json | CSR disc1 layer |

If you still have ff7_d1_csr_noswap_work.bin, that is the same role as core work (copy/rename optional).

## Packs (builder)

| Pack id | Role |
|---------|------|
| single-disc-on-csr-v0.1.1 | Core vs csr-v0.14.1 |
| single-disc-csr-manip-movies-v0.1.0 | Movies vs (CSR + core) |

Stack for CSR-alone single-disc:

    Base: csr-v0.14.1
    + single-disc-on-csr-v0.1.1
    + single-disc-csr-manip-movies-v0.1.0
    CSR+ scenes: OFF

---

## Phase A — baselines

    cd /path/to/Final-Fantasy-7-Modding
    git pull --ff-only

Apply CSR base if ff7_d1_csr_base.bin missing or stale (run in repo root):

    python3 scripts/apply_layer.py workspace/pristine/FINALFANTASY7_D1.bin \
      /Users/david.morton/Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json \
      -o workspace/iso-extract/ff7_d1_csr_base.bin

If apply_layer.py CLI differs, use:

    python3 -c "import json,sys; from pathlib import Path; sys.path.insert(0,"scripts"); from apply_layer import apply_layer; pr=Path("workspace/pristine/FINALFANTASY7_D1.bin").read_bytes(); layer=json.loads(Path("/Users/david.morton/Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json").read_text()); img=bytearray(pr); apply_layer(img, layer); Path("workspace/iso-extract/ff7_d1_csr_base.bin").write_bytes(bytes(img)); print(len(img))"

Core work — pick one:

    # Fresh from CSR base (then you must re-do ALL core Makou + SNOVA; rare)
    cp -f workspace/iso-extract/ff7_d1_csr_base.bin workspace/iso-extract/ff7_d1_csr_single_disc_core_work.bin

    # Preferred if you already have core work (field trims + SNOVA):
    cp -f workspace/iso-extract/ff7_d1_csr_noswap_work.bin workspace/iso-extract/ff7_d1_csr_single_disc_core_work.bin

---

## Phase B — Makou BLACKBGB (required for complete core)

Open: workspace/iso-extract/ff7_d1_csr_single_disc_core_work.bin

1. Field blackbgb
2. Remove every Ask for disc (DSKCG)
3. Keep CSR jumps, bit clears, conditions, map jumps
4. Do NOT paste Clean BLACKBGB over CSR (wipes CSR hub)
5. Save FIELD into the same work bin

---

## Phase C — SNOVA (only if this work bin never had SNOVA)

Skip if size already about 748775664 and SNOVA was injected earlier.

    python3 mods/single-disc/scripts/inject_snova_d3_to_d1.py \
      --d1 workspace/iso-extract/ff7_d1_csr_single_disc_core_work.bin \
      --d3 workspace/pristine/FINALFANTASY7_D3.bin \
      --in-place

Expect: raw-copy + BATTLE.X LBA patch v3; 17 LBA entries; SNOVA verify OK.

---

## Phase D — rebuild core pack layer

Diff core work vs CSR base (not pristine Clean):

    python3 -c "import json,sys; from pathlib import Path; sys.path.insert(0,"scripts"); from bin_diff_to_layer import build_layer; base=Path("workspace/iso-extract/ff7_d1_csr_base.bin"); work=Path("workspace/iso-extract/ff7_d1_csr_single_disc_core_work.bin"); out=Path("builder/single-disc-on-csr-v0.1.1/layers/disc1.layer.json"); layer=build_layer(base, work, layer_id="single-disc-on-csr-v0.1.1-disc1", description="Single-disc on CSR D1 after BLACKBGB Makou"); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(layer, indent=2)+chr(10)); print(layer["stats"])"

---

## Phase E — verify core alone

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base csr-v0.14.1 \
      --addon single-disc-on-csr-v0.1.1 \
      --csr-root /Users/david.morton/Final-Fantasy-7-CSR

Must print PASS.

---

## Phase F — movie seed on top of new core

    python3 -c "import json,sys; from pathlib import Path; sys.path.insert(0,"scripts"); from apply_layer import apply_layer; pr=Path("workspace/pristine/FINALFANTASY7_D1.bin").read_bytes(); csr=json.loads(Path("/Users/david.morton/Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json").read_text()); core=json.loads(Path("builder/single-disc-on-csr-v0.1.1/layers/disc1.layer.json").read_text()); img=bytearray(pr); apply_layer(img,csr); apply_layer(img,core); Path("workspace/iso-extract/ff7_d1_csr_single_disc_core_applied.bin").write_bytes(bytes(img)); print(len(img))"

    cp -f workspace/iso-extract/ff7_d1_csr_single_disc_core_applied.bin \
          workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin

    python3 mods/single-disc/scripts/inject_movies_by_disc_id.py \
      --d1 workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin \
      --manifest mods/single-disc/patches/csr-manip-movie-seed.txt \
      --in-place

Expect four OK lines (ids 36, 34, 37, 7).

---

## Phase G — rebuild movie pack layer

    python3 -c "import json,sys; from pathlib import Path; sys.path.insert(0,"scripts"); from bin_diff_to_layer import build_layer; base=Path("workspace/iso-extract/ff7_d1_csr_single_disc_core_applied.bin"); work=Path("workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin"); out=Path("builder/single-disc-csr-manip-movies-v0.1.0/layers/disc1.layer.json"); layer=build_layer(base, work, layer_id="single-disc-csr-manip-movies-v0.1.0-disc1", description="CSR single-disc manip movie seed"); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(layer, indent=2)+chr(10)); print(layer["stats"])"

---

## Phase H — verify full stack

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base csr-v0.14.1 \
      --addon single-disc-on-csr-v0.1.1 \
      --addon single-disc-csr-manip-movies-v0.1.0 \
      --csr-root /Users/david.morton/Final-Fantasy-7-CSR

Must print PASS.

Optional built image for DuckStation:

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base csr-v0.14.1 \
      --addon single-disc-on-csr-v0.1.1 \
      --addon single-disc-csr-manip-movies-v0.1.0 \
      --csr-root /Users/david.morton/Final-Fantasy-7-CSR \
      -o workspace/iso-extract/ff7_d1_csr_single_disc_full_built.bin

---

## Phase I — playtest

### Local bin

DuckStation: ff7_d1_csr_single_disc_full_built.bin or ff7_d1_csr_single_disc_movies_work.bin (Disc 1 only).

### Site builder (after Phase J Pages deploy)

https://individualcontributor.dev/builder/

1. Load pristine NTSC-U Disc 1 .bin
2. Base: CSR v0.14.1
3. Enable: Single-disc on CSR v0.1.1 + CSR manip movies seed v0.1.0
4. CSR+ scenes: all off
5. Build; smoke emulator (EDC repair before optical burn as usual)

### Checks

- Boot / early game OK
- blackbgb: no Ask for disc
- Supernova OK
- Seed movies if you reach those scenes
- Other wrong/crawl FMV: note name + map in mods/single-disc/patches/csr-manip-movie-whitelist.md

---

## Phase J — publish

    git pull --ff-only
    git add builder/single-disc-on-csr-v0.1.1 \
            builder/single-disc-csr-manip-movies-v0.1.0 \
            builder/manifest.json \
            mods/single-disc/ \
            docs/
    git status
    git commit -m "single-disc: CSR core after BLACKBGB + refresh movie seed pack"
    git push

Do not commit workspace/**/*.bin.

---

## Phase K — agent check

Say check and paste evidence. Agent pulls and re-verifies full stack against the repo packs.

---

## Checklist

- [ ] A baselines
- [ ] B Makou BLACKBGB
- [ ] C SNOVA if needed
- [ ] D rebuild core layer
- [ ] E verify core PASS
- [ ] F inject movies
- [ ] G rebuild movie layer
- [ ] H verify full stack PASS
- [ ] I playtest
- [ ] J commit push
- [ ] K say check

## Evidence

    git pull:
    BLACKBGB Makou:
    SNOVA skipped or ran:
    core layer stats:
    verify core:
    movies inject lines:
    movie layer stats:
    verify full:
    -o built path:
    playtest notes:
    push:
