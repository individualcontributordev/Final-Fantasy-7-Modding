# Task: LAS4_2 movie trim shipped without Makou

## Done just now

Field 765 / LAS4_2 wrong FMV on CSR+single-disc: Makou invalid archive when deleting Set movie on grown single-disc bins.

Fix published in pack: reused Clean single-disc pre-trimmed FIELD/LAS4_2.DAT (Set+Play already removed) onto single-disc-on-csr-v0.1.1 via ISO pad-replace + layer rebuild. CSR D1 never edits this map (bytes match pristine), so Clean trim is safe.

- Verify: PASS (csr-v0.14.1 + single-disc-on-csr-v0.1.1)
- Do not need Makou for 765 anymore on a new builder zip.

## Still use Makou only for CSR-unique maps

e.g. BLACKBGB (#103) Ask deletes — CSR edits that hub; cannot paste Clean.

When Makou is required: edit on a fresh CSR base + pack layer apply; avoid repeated save on SNOVA-grown playtest bins.

---

# Task: publish Makou-fixed single-disc-on-csr pack

Your edits are on the other machine. Put the fixed work bin here, rebuild the layer, verify, push. Then rebuild a zip on the site and keep playtesting.

## 0. What this pack is

- Repo: Final-Fantasy-7-Modding
- Pack id: single-disc-on-csr-v0.1.1
- Layer: builder/single-disc-on-csr-v0.1.1/layers/disc1.layer.json
- Diff baseline: CSR D1 only (not pristine Clean)
- Site CDN: this repo GitHub Pages (builder loads remote Modding manifest)

## 1. Copy the work bin onto this machine

Expected path (gitignored):

    workspace/iso-extract/ff7_d1_csr_single_disc_playtest_work.bin

That file must already include:

- CSR base
- Single-disc field work (D2/D3 CSR field merge, SNOVA if kept in the same bin)
- Latest Makou edits (blackbgb Ask deleted, no forward/JMPF; LAS4_2 etc. Set+Play as needed)

If the file has another name, copy/rename to the path above or change WORK in the commands below.

Also ensure CSR baseline exists:

    workspace/iso-extract/ff7_d1_csr_base.bin

Rebuild CSR base if missing:

    python3 scripts/apply_layer.py \
      workspace/pristine/FINALFANTASY7_D1.bin \
      ../Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json \
      -o workspace/iso-extract/ff7_d1_csr_base.bin

Pristine D1 must exist at workspace/pristine/FINALFANTASY7_D1.bin.

## 2. Rebuild the builder layer

From Final-Fantasy-7-Modding root:

    git pull --ff-only

    python3 scripts/bin_diff_to_layer.py \
      workspace/iso-extract/ff7_d1_csr_base.bin \
      workspace/iso-extract/ff7_d1_csr_single_disc_playtest_work.bin \
      -o builder/single-disc-on-csr-v0.1.1/layers/disc1.layer.json \
      --id single-disc-on-csr-v0.1.1-disc1 \
      --description "Single-disc on CSR D1: Ask delete, field merges, movie trims, SNOVA"

Do not diff against pristine Clean. Baseline is always ff7_d1_csr_base.bin.

## 3. Verify (required)

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 \
      --base csr-v0.14.1 \
      --addon single-disc-on-csr-v0.1.1

Optional (CSR + single-disc + movie seed, no CSR+):

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 \
      --base csr-v0.14.1 \
      --addon single-disc-on-csr-v0.1.1 \
      --addon single-disc-csr-manip-movies-v0.1.0

Must print PASS.

## 4. Changelog + commit + push

Edit mods/single-disc/CHANGELOG.md (Unreleased or new section), e.g.:

- blackbgb (#103): delete four Ask-for-disc ops (remove bad JMPF/forward stubs)
- LAS4_2 (#765) / other maps: delete Set+Play where wrong FMV on D1
- (list anything else you fixed in Makou)

Then:

    git add builder/single-disc-on-csr-v0.1.1/layers/disc1.layer.json \
            mods/single-disc/CHANGELOG.md \
            docs/INSTRUCTIONS.md

    git commit -m "single-disc-on-csr: publish Makou field fixes (blackbgb, movies)"
    git pull --rebase
    git push

Wait for GitHub Pages on this repo (often 1-2 minutes).

## 5. New zip + continue testing

1. Hard-refresh https://individualcontributor.dev/builder/
2. Base: CSR · Mods: Single-disc (movie pack auto if no CSR+)
3. Build zip from a clean pristine D1 .bin (not the old work bin)
4. Playtest; next Makou pass: edit a fresh apply (CSR base + new pack layer), not a sick re-saved grown bin

### Fresh Makou source next time (avoid invalid archive)

    python3 scripts/apply_layer.py \
      workspace/pristine/FINALFANTASY7_D1.bin \
      ../Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json \
      -o workspace/iso-extract/ff7_d1_csr_base.bin

    python3 scripts/apply_layer.py \
      workspace/iso-extract/ff7_d1_csr_base.bin \
      builder/single-disc-on-csr-v0.1.1/layers/disc1.layer.json \
      -o workspace/iso-extract/ff7_d1_csr_single_disc_makou_work.bin

Open ff7_d1_csr_single_disc_makou_work.bin in Makou once, edit, save once, then repeat steps 2-4.

## Makou checklist (already partly done)

| ID | Map | Edit |
|---:|-----|------|
| 103 | BLACKBGB | Delete four Ask-for-disc; remove any forward/JMPF; keep music + jumps |
| 765 | LAS4_2 | Delete Set next movie + Play movie if wrong FMV |
| 763/766/767/768 | LAS4_* / LASTMAP | Same movie trim if wrong/crawl |
| 95/106 | BLACKBG3/E | Delete Ask if still present |

Keep Wait / Execute / Jump / bits. Do not use FIELD.BIN DSKCG stubs.

## Priority field ids (spot-check)

95 BLACKBG3 · 103 BLACKBGB · 106 BLACKBGE · 67 FSHIP_12 · 68 FSHIP_2 · 269 BLIN70_4 · 347 FR_E · 634 LOST2 · 637 LOSLAKE1 · 643 WHITE2 · 695 GAIA_32 · 725-727 ZMIND* · 744 LAS0_1 · 751 LAS0_8 · 763/765/766/767 LAS4_* · 768 LASTMAP · 777 LAS4_42 · 779 MD8_52

## Notes for check

    Work bin path:
    bin_diff:
    verify PASS:
    commit:
    Builder zip:
    After Hojo / las0_1:
    LAS4_2 FMV:
    Other:
