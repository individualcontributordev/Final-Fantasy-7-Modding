# Task: CSR single-disc — after blackbgb edit (rebuild packs)

## Why only blackbgb?

The core pack already fixed **Ask for disc** (and freeze-on-missing-video) on every other map we needed by copying those map files from the proven Clean single-disc work.

**blackbgb is different:** CSR itself already changed that map (hub / routing). We could not drop the Clean file on top without wiping CSR. So blackbgb was left as the CSR version, which still had **Ask for disc**.

Your Makou edit is only for that leftover: remove Ask on **blackbgb** on a CSR + single-disc image. You do not need to re-edit the other maps.

---

## Already done before your edit

| Pack | Status |
|------|--------|
| single-disc-on-csr-v0.1.1 | Published (other maps + Supernova; blackbgb was still CSR) |
| single-disc-csr-manip-movies-v0.1.0 | Published (4 videos) |

Playtest stack you used:

    CSR v0.14.1
    + Single-disc (on CSR) v0.1.1
    + Movies seed v0.1.0
    + No CSR+

---

## Done by you

- [x] Makou on that same playtest Disc 1: blackbgb — remove Ask for disc; keep CSR jumps/flags

---

## What you do next (update the published packs)

You edited a builder zip .bin. That file is not in git. Rebuild the pack layers from it, then push, then a **new** builder zip to play.

### 1. Paths

    WORK = full path to your Makoued Disc 1 .bin (the one you just saved)
    CSR repo layer = /Users/david.morton/Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json

### 2. CSR base (comparison only)

    cd /path/to/Final-Fantasy-7-Modding
    git pull --ff-only

    python3 scripts/apply_layer.py workspace/pristine/FINALFANTASY7_D1.bin \
      /Users/david.morton/Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json \
      -o workspace/iso-extract/ff7_d1_csr_base.bin

### 3. Rebuild core pack from your WORK bin

    python3 -c "import json,sys; from pathlib import Path; sys.path.insert(0,"scripts"); from bin_diff_to_layer import build_layer; base=Path("workspace/iso-extract/ff7_d1_csr_base.bin"); work=Path("WORK"); out=Path("builder/single-disc-on-csr-v0.1.1/layers/disc1.layer.json"); layer=build_layer(base, work, layer_id="single-disc-on-csr-v0.1.1-disc1", description="Single-disc on CSR after blackbgb Ask removed"); out.write_text(json.dumps(layer, indent=2)+chr(10)); print(layer["stats"])"

Replace WORK with your real path in quotes.

### 4. Check core

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base csr-v0.14.1 \
      --addon single-disc-on-csr-v0.1.1 \
      --csr-root /Users/david.morton/Final-Fantasy-7-CSR

Must say PASS.

### 5. Put the four videos back on the new core

(Your WORK bin may already include the movie seed if you edited the full playtest image. Rebuilding the movie pack still needs a clean "core only" image + inject, or diff WORK against core-applied if WORK is core+movies+blackbgb.)

**If WORK is the full playtest image (core + movies + your blackbgb edit):**

    # Image with new core only (no movies), for movie pack baseline
    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base csr-v0.14.1 \
      --addon single-disc-on-csr-v0.1.1 \
      --csr-root /Users/david.morton/Final-Fantasy-7-CSR \
      -o workspace/iso-extract/ff7_d1_csr_single_disc_core_applied.bin

    # Rebuild movie pack: full WORK minus new core-only image
    python3 -c "import json,sys; from pathlib import Path; sys.path.insert(0,"scripts"); from bin_diff_to_layer import build_layer; base=Path("workspace/iso-extract/ff7_d1_csr_single_disc_core_applied.bin"); work=Path("WORK"); out=Path("builder/single-disc-csr-manip-movies-v0.1.0/layers/disc1.layer.json"); layer=build_layer(base, work, layer_id="single-disc-csr-manip-movies-v0.1.0-disc1", description="CSR single-disc extra videos (unchanged seed)"); out.write_text(json.dumps(layer, indent=2)+chr(10)); print(layer["stats"])"

Again replace WORK with your Makoued .bin path.

**If WORK is core-only (no movies):** inject movies after step 4 onto a copy of core-applied, then diff that against core-applied (same as before).

### 6. Check full stack

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base csr-v0.14.1 \
      --addon single-disc-on-csr-v0.1.1 \
      --addon single-disc-csr-manip-movies-v0.1.0 \
      --csr-root /Users/david.morton/Final-Fantasy-7-CSR

Must say PASS.

### 7. Publish

    git add builder/single-disc-on-csr-v0.1.1 \
            builder/single-disc-csr-manip-movies-v0.1.0 \
            builder/manifest.json \
            docs/INSTRUCTIONS.md
    git commit -m "single-disc: CSR core after blackbgb Ask removed"
    git push

Do not commit .bin or builder zips.

### 8. New builder zip and play again

Same stack as before. Confirm blackbgb no longer asks for a disc.

Say **check** when pushed (or paste verify output if something fails).

---

## Notes for check

    WORK bin was: full playtest (core+movies) / core only
    Core layer rebuild stats:
    Movie layer rebuild stats:
    verify core:
    verify full:
    push:
    blackbgb ask gone on new zip:
