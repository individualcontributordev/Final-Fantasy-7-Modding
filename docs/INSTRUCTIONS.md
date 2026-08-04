# Task: CSR single-disc — what is done vs what you do

## Already done (use the builder — do not rebuild these)

On the website builder, enabled and ready:

| What you pick | Pack name in the list |
|---------------|------------------------|
| CSR base | CSR v0.14.1 |
| Single disc core | Single-disc (on CSR) v0.1.1 |
| Extra cutscene videos for CSR | Single-disc CSR manip movies v0.1.0 (seed) |

**Core pack already includes:**
- Stops the game asking you to insert Disc 2 or 3
- Stops freezes when a cutscene video is missing on Disc 1 (on the maps we already fixed)
- Makes the Supernova boss fight work on Disc 1

**Movie pack already includes** these videos on Disc 1 (for CSR without the CSR+ scene packs):
- LASTFLOR.MOV
- LAST4_3.BIN
- LASTMAP.BIN
- CANONHT2.MOV

**Still not finished in the core pack:**
- The blackbgb map may still ask for another disc (needs a Makou edit on the CSR version of that map — see Later, only if needed)

Clean / Unmodified single-disc pack is turned off on purpose. Do not use it for CSR.

---

## What you do now

1. Open https://individualcontributor.dev/builder/
2. Load a normal NTSC-U Disc 1 .bin
3. Choose:
   - Base: **CSR v0.14.1**
   - **Single-disc (on CSR) v0.1.1**
   - **Single-disc CSR manip movies seed v0.1.0**
   - Do **not** turn on CSR+ scene packs for this test
4. Build and download the zip (it will be outside this project folder; the name comes from the base and mods)
5. Play that Disc 1 image in DuckStation (or burn later if you want)

You do **not** need to rebuild or publish packs for this step. They are already published.

---

## What to watch for while playing

- Does the game boot and play normally?
- Does it still stop and ask for Disc 2 or 3? Which map?
- Does Supernova work?
- Do the four added videos look OK if you reach those scenes?
- Anywhere the game freezes or crawls on a cutscene? Note the map name and, if you know it, the video file name.

When you are done testing, say **check** and paste short notes.

---

## Later, only if needed

### A. blackbgb still asks for a disc

Only then edit and update the **existing** core pack (not a brand new mod from scratch).

1. Build a zip: CSR + Single-disc on CSR only (movie pack optional).
2. Open that Disc 1 .bin in Makou.
3. On map **blackbgb**, delete **Ask for disc** only. Leave CSR jumps and flags alone. Do not paste the Clean map over CSR.
4. Save into the same .bin.
5. Rebuild the core pack layer from that .bin against CSR base, verify, then put the four videos back on top and rebuild the movie pack, verify, commit and push.
6. Build a **new** zip from the website and test again.

Full commands for that rebuild are at the bottom under Rebuild commands.

### B. You need more cutscene videos on Disc 1

1. Write down map + video name from your playtest.
2. Add a line to mods/single-disc/patches/csr-manip-movie-seed.txt
3. Re-run the movie inject and rebuild only the movie pack (commands below).
4. Push, then a new builder zip.

---

## Simple picture

    Website builder zip  =  how you play
    Packs in git         =  already made for CSR + single disc (+ optional videos)
    Makou / rebuild      =  only when something is still wrong after playtest

    Clean disc you burned before  =  old test on normal game, not the CSR pack baseline

---

## Rebuild commands (only after Makou or more videos)

Set WORK to your edited Disc 1 .bin path.

CSR base image (for comparison only):

    python3 scripts/apply_layer.py workspace/pristine/FINALFANTASY7_D1.bin \
      /Users/david.morton/Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json \
      -o workspace/iso-extract/ff7_d1_csr_base.bin

Update core pack after blackbgb edit (WORK = your Makoued file):

    python3 -c "import json,sys; from pathlib import Path; sys.path.insert(0,"scripts"); from bin_diff_to_layer import build_layer; base=Path("workspace/iso-extract/ff7_d1_csr_base.bin"); work=Path("WORK"); out=Path("builder/single-disc-on-csr-v0.1.1/layers/disc1.layer.json"); layer=build_layer(base, work, layer_id="single-disc-on-csr-v0.1.1-disc1", description="Single-disc on CSR after blackbgb edit"); out.write_text(json.dumps(layer, indent=2)+chr(10)); print(layer["stats"])"

    python3 scripts/verify_builder_config.py --pristine workspace/pristine/FINALFANTASY7_D1.bin --disc 1 --base csr-v0.14.1 --addon single-disc-on-csr-v0.1.1 --csr-root /Users/david.morton/Final-Fantasy-7-CSR

Refresh videos on top of the new core:

    python3 scripts/verify_builder_config.py --pristine workspace/pristine/FINALFANTASY7_D1.bin --disc 1 --base csr-v0.14.1 --addon single-disc-on-csr-v0.1.1 --csr-root /Users/david.morton/Final-Fantasy-7-CSR -o workspace/iso-extract/ff7_d1_csr_single_disc_core_applied.bin

    cp -f workspace/iso-extract/ff7_d1_csr_single_disc_core_applied.bin workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin

    python3 mods/single-disc/scripts/inject_movies_by_disc_id.py --d1 workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin --manifest mods/single-disc/patches/csr-manip-movie-seed.txt --in-place

    python3 -c "import json,sys; from pathlib import Path; sys.path.insert(0,"scripts"); from bin_diff_to_layer import build_layer; base=Path("workspace/iso-extract/ff7_d1_csr_single_disc_core_applied.bin"); work=Path("workspace/iso-extract/ff7_d1_csr_single_disc_movies_work.bin"); out=Path("builder/single-disc-csr-manip-movies-v0.1.0/layers/disc1.layer.json"); layer=build_layer(base, work, layer_id="single-disc-csr-manip-movies-v0.1.0-disc1", description="CSR single-disc extra videos"); out.write_text(json.dumps(layer, indent=2)+chr(10)); print(layer["stats"])"

    python3 scripts/verify_builder_config.py --pristine workspace/pristine/FINALFANTASY7_D1.bin --disc 1 --base csr-v0.14.1 --addon single-disc-on-csr-v0.1.1 --addon single-disc-csr-manip-movies-v0.1.0 --csr-root /Users/david.morton/Final-Fantasy-7-CSR

    git add builder/single-disc-on-csr-v0.1.1 builder/single-disc-csr-manip-movies-v0.1.0 builder/manifest.json
    git commit -m "single-disc: update CSR core and video pack after edits"
    git push

Do not commit .bin files or builder zips.

---

## Notes for check

    Built zip with CSR + core + movies: yes/no
    Boot OK:
    Still asks for another disc? where:
    Supernova:
    Videos OK / wrong:
    Freeze or crawl (map + video if known):
    blackbgb edit done: no / yes and pushed:
