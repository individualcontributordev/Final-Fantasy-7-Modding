# Task: No-disc-swap on CSR base (Clean assumed OK)

## Assumption

Clean no-disc-swap-clean-v0.1.1 works. Next: same mod for CSR base.

Live base ids to verify on CSR Pages (this clone saw):

- CSR: csr-v0.14.1
- Highwind (later): highwind-v0.2.0

## Goal

Builder add-on: no-disc-swap-on-csr-v0.1.1

- compatibleBases: ["csr-v0.14.1"]
- Disc 1 only
- exclusiveGroup: no-disc-swap (one no-disc-swap choice at a time)

## Must include

| Piece | Notes |
|-------|--------|
| Ask-for-disc removal | Makou on CSR FIELD, not Clean layer paste |
| Field Set+Play movie trims | Same sites as Clean where ops still exist on CSR |
| SNOVA + BATTLE.X LBA remap | Required for any no-disc-swap (battle module) |
| Field FMV file copies | Default none; CSR manip copy only on FAIL |

Clean layer JSON must not be applied onto CSR — FIELD bytes differ.

## Steps

### 1. CSR baseline Disc 1 image

    cd Final-Fantasy-7-Modding
    git pull --ff-only

Get CSR-only D1 (builder: Base=CSR, no no-disc-swap), save as:

    workspace/iso-extract/ff7_d1_csr_base.bin

    cp -f workspace/iso-extract/ff7_d1_csr_base.bin \
          workspace/iso-extract/ff7_d1_csr_noswap_work.bin

### 2. Makou on CSR work bin

Open ff7_d1_csr_noswap_work.bin.

1. Ask for disc — Find All; delete DSKCG; keep jumps/bits
   (blackbgb / blackbg3 / blackbge + any CSR-only hits)
2. Set next movie + Play movie — same trims as Clean where still present
   (lists under mods/no-disc-swap/patches/)
3. Save into work bin

### 3. SNOVA (always with no-disc-swap)

    python3 mods/no-disc-swap/scripts/inject_snova_d3_to_d1.py \
      --d1 workspace/iso-extract/ff7_d1_csr_noswap_work.bin \
      --d3 workspace/pristine/FINALFANTASY7_D3.bin \
      --in-place

Expect: BATTLE.X LBA patch v3; 17 LBA entries remapped.

### 4. Layer = CSR work minus CSR baseline

Diff baseline CSR bin to work bin (NOT pristine Clean):

    python3 mods/no-disc-swap/scripts/build_clean_d1_layer.py \
      --work workspace/iso-extract/ff7_d1_csr_noswap_work.bin \
      --pristine workspace/iso-extract/ff7_d1_csr_base.bin \
      --version 0.1.1

Script still names pack no-disc-swap-clean-v0.1.1 by default. Then fix:

    mkdir -p builder/no-disc-swap-on-csr-v0.1.1/layers
    mv builder/no-disc-swap-clean-v0.1.1/layers/disc1.layer.json \
       builder/no-disc-swap-on-csr-v0.1.1/layers/
    # remove empty clean dir if it was a fresh build artifact only

Edit builder/manifest.json — add/enable:

    id: no-disc-swap-on-csr-v0.1.1
    name: No-disc-swap (CSR) v0.1.1
    compatibleBases: ["csr-v0.14.1"]
    discs.1: ./no-disc-swap-on-csr-v0.1.1/layers/disc1.layer.json
    exclusiveGroup: no-disc-swap
    enabled: true

Keep no-disc-swap-clean-v0.1.1 enabled for Clean users.

Optional later: extend build script with --against csr.

### 5. Verify

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base csr-v0.14.1 \
      --addon no-disc-swap-on-csr-v0.1.1

Must PASS.

### 6. Push

    git add builder/no-disc-swap-on-csr-v0.1.1 builder/manifest.json mods/no-disc-swap
    git -c user.email=contributorindividual@gmail.com -c user.name=individualcontributordev \
      commit -m "no-disc-swap 0.1.1: CSR base pack"
    git push

### 7. Playtest

Builder: Base CSR + No-disc-swap (CSR). Prefer D1-origin saves.
Smoke: asks, movie crawl sites, Supernova if possible.

## After CSR OK

1. CSR + CSR+ scene add-ons (SNOVA already in no-disc-swap pack)
2. Highwind: same recipe vs Highwind baseline -> no-disc-swap-on-highwind-v0.1.1

## Evidence

    CSR base id:
    Makou Ask + movie trims: yes/no
    SNOVA: PASS/FAIL
    verify: PASS/FAIL
    DS smoke: PASS/FAIL
    Published: yes/no

Say check.

