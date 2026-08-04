# Task: CSR single-disc — what is DONE vs what you do next

## Already done (do not rebuild/publish unless you changed something)

These are on git main, manifest **enabled**, available to the builder after Pages deploy:

| Pack | Id | Status |
|------|-----|--------|
| CSR single-disc **core** | single-disc-on-csr-v0.1.1 | **Published** — Ask/crawl field trims (from Clean recipe on CSR maps) + SNOVA/BATTLE.X. Label says partial only because BLACKBGB Ask on CSR script is still open. |
| CSR manip **movies** seed | single-disc-csr-manip-movies-v0.1.0 | **Published** — LASTFLOR, LAST4_3, LASTMAP, CANONHT2 by PMVIE id. |
| Clean single-disc | single-disc-clean-v0.1.1 | Published but **disabled** (retired). |

Verified stack (agent already ran):

    csr-v0.14.1
    + single-disc-on-csr-v0.1.1
    + single-disc-csr-manip-movies-v0.1.0
    → PASS

**Your playtest path now:** site builder only — fresh zip, no rebuild.

    Base: CSR v0.14.1
    Single-disc on CSR v0.1.1
    CSR manip movies seed v0.1.0
    CSR+ scenes: off

https://individualcontributor.dev/builder/

---

## Not done (only your next real work)

1. **Playtest** the published stack (builder zip).
2. **Optional later — BLACKBGB on CSR:** Makou remove Ask for disc on blackbgb **using a bin from a builder zip of CSR + core**, then rebuild core pack + refresh movie pack + push.  
   → Use **Appendix: redo after BLACKBGB** only when you do this. Not required to start playtest.
3. **Optional later — more movies:** after playtest notes, extend seed list and rebuild movie pack only.

Do **not** re-run core/movie pack creation from scratch. Do **not** use Clean console bins as CSR baseline.

---

## Playtest notes (paste when you say check)

    Builder zip stack: CSR + core + movies seed (yes/no)
    Boot OK:
    Ask for disc still? where:
    Supernova:
    Seed FMVs OK / wrong:
    Other crawl or missing FMV (name + map):
    BLACKBGB Makou done: no (default) / yes + pushed:

---

## Appendix: redo after BLACKBGB (only if you edit FIELD)

Only when pack **content** must change. Packs already exist — this **updates** them.

1. Builder zip (or verify -o): CSR + single-disc-on-csr only → Disc 1 .bin
2. Makou blackbgb: remove Ask; keep CSR jumps; save into that .bin
3. Diff that .bin vs CSR base → overwrite builder/single-disc-on-csr-v0.1.1/layers/disc1.layer.json
4. verify core PASS
5. Apply CSR+new core → inject seed movies → rebuild single-disc-csr-manip-movies-v0.1.0 layer
6. verify full stack PASS
7. git commit push packs only (no .bin)
8. New builder zip to playtest

Commands (paths: set WORK to your Makoued .bin):

    # CSR base (diff baseline only)
    python3 scripts/apply_layer.py workspace/pristine/FINALFANTASY7_D1.bin \
      /Users/david.morton/Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json \
      -o workspace/iso-extract/ff7_d1_csr_base.bin

    # Rebuild core layer (WORK = Makoued bin)
    python3 -c "import json,sys; from pathlib import Path; sys.path.insert(0,"scripts"); from bin_diff_to_layer import build_layer; base=Path("workspace/iso-extract/ff7_d1_csr_base.bin"); work=Path("WORK"); out=Path("builder/single-disc-on-csr-v0.1.1/layers/disc1.layer.json"); layer=build_layer(base, work, layer_id="single-disc-on-csr-v0.1.1-disc1", description="Single-disc on CSR after BLACKBGB"); out.write_text(json.dumps(layer, indent=2)+chr(10)); print(layer["stats"])"

    python3 scripts/verify_builder_config.py --pristine workspace/pristine/FINALFANTASY7_D1.bin --disc 1 --base csr-v0.14.1 --addon single-disc-on-csr-v0.1.1 --csr-root /Users/david.morton/Final-Fantasy-7-CSR

    python3 scripts/verify_builder_config.py --pristine workspace/pristine/FINALFANTASY7_D1.bin --disc 1 --base csr-v0.14.1 --addon single-disc-on-csr-v0.1.1 --csr-root /Users/david.morton/Final-Fantasy-7-CSR -o workspace/iso-extract/ff7_d1_csr_single_disc_core_applied.bin

    cp -f workspace/iso-extract/ff7_d1_csr_single_disc_core_applied.bin workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin

    python3 mods/single-disc/scripts/inject_movies_by_disc_id.py --d1 workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin --manifest mods/single-disc/patches/csr-manip-movie-seed.txt --in-place

    python3 -c "import json,sys; from pathlib import Path; sys.path.insert(0,"scripts"); from bin_diff_to_layer import build_layer; base=Path("workspace/iso-extract/ff7_d1_csr_single_disc_core_applied.bin"); work=Path("workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin"); out=Path("builder/single-disc-csr-manip-movies-v0.1.0/layers/disc1.layer.json"); layer=build_layer(base, work, layer_id="single-disc-csr-manip-movies-v0.1.0-disc1", description="CSR manip movie seed"); out.write_text(json.dumps(layer, indent=2)+chr(10)); print(layer["stats"])"

    python3 scripts/verify_builder_config.py --pristine workspace/pristine/FINALFANTASY7_D1.bin --disc 1 --base csr-v0.14.1 --addon single-disc-on-csr-v0.1.1 --addon single-disc-csr-manip-movies-v0.1.0 --csr-root /Users/david.morton/Final-Fantasy-7-CSR

    git add builder/single-disc-on-csr-v0.1.1 builder/single-disc-csr-manip-movies-v0.1.0 builder/manifest.json
    git commit -m "single-disc: CSR core after BLACKBGB + movie seed refresh"
    git push
