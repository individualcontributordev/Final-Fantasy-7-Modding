# Task: Build no-disc-swap for CSR+ and Highwind (CSR base deferred)

## Policy

| Stack | no-disc-swap now? |
|-------|-------------------|
| Unmodified | No |
| CSR base alone + manip movies | **Defer** (disc size) |
| CSR + CSR+ | **Yes - build now** |
| Highwind | **Yes - build now** |

CSR+ removes field FMVs; Highwind trims cutscenes. Core pack only:

- Ask-for-disc Makou removal (vs that base FIELD)
- Field Set+Play trims where crawl still happens
- SNOVA + BATTLE.X LBA inject
- No D2/D3 manip movie file copies

Live base ids (verify on CSR Pages): csr-v0.14.1, highwind-v0.2.0

## Pack targets

1. no-disc-swap-on-csr-v0.1.1
   - compatibleBases: [csr-v0.14.1]
   - Used with CSR+ scene add-ons (and alone later when manip pack exists)
2. no-disc-swap-on-highwind-v0.1.1
   - compatibleBases: [highwind-v0.2.0]

## Recipe (each base)

### A. Baseline D1 image

Builder or layer apply:

- CSR: pristine + csr-v0.14.1 disc1 layer -> workspace/iso-extract/ff7_d1_csr_base.bin
- Highwind: pristine + highwind-v0.2.0 disc1 layer -> workspace/iso-extract/ff7_d1_hw_base.bin

### B. Work copy + Makou

    cp -f BASE.bin workspace/iso-extract/ff7_d1_BASE_noswap_work.bin

Makou on work bin:

1. Remove all Ask for disc (keep jumps/bits)
2. Remove Set next movie + Play movie on same sites as Clean playtest
   (CSR+/HW may already lack some; trim what remains / crawls)
3. Save FIELD into work bin

### C. SNOVA

    python3 mods/no-disc-swap/scripts/inject_snova_d3_to_d1.py \
      --d1 WORK.bin \
      --d3 workspace/pristine/FINALFANTASY7_D3.bin \
      --in-place

### D. Layer vs baseline (not pristine Clean)

    python3 mods/no-disc-swap/scripts/build_clean_d1_layer.py \
      --work WORK.bin \
      --pristine BASE.bin \
      --version 0.1.1

Then rename pack dir + manifest:

- id / path: no-disc-swap-on-csr-v0.1.1 or no-disc-swap-on-highwind-v0.1.1
- compatibleBases: csr-v0.14.1 or highwind-v0.2.0
- enabled: true
- exclusiveGroup: no-disc-swap

### E. Verify + push

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base csr-v0.14.1 \
      --addon no-disc-swap-on-csr-v0.1.1

    # and/or highwind-v0.2.0 + no-disc-swap-on-highwind-v0.1.1

CSR+ stack check example:

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base csr-v0.14.1 \
      --addon csr-plus-scene-... --addon no-disc-swap-on-csr-v0.1.1

(Use real CSR+ addon ids from CSR manifest.)

Commit builder packs + manifest; push; builder smoke + burn.

## Order of work

1. Highwind (simpler - one base, aggressive trims)
2. CSR core pack for use with CSR+
3. Later: CSR manip-movie pack + CSR-alone stack

## Evidence

    HW pack: built/published/verified
    CSR pack: built/published/verified
    CSR+ stack smoke:
    Notes:

Say check.
