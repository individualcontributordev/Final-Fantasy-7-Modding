# Task: Publish no-disc-swap **0.1.1** release (no -dev)

## Goal

Ship builder pack **no-disc-swap-clean-v0.1.1** from your combined work bin,
then burn and console-confirm.

VERSION in repo is already **0.1.1**.

## On PC with work bin (Ask + all movie trims + SNOVA v3)

    cd Final-Fantasy-7-Modding
    git pull --ff-only

    # if SNOVA not on work bin yet:
    # python3 mods/no-disc-swap/scripts/inject_snova_d3_to_d1.py \
    #   --d1 WORK.bin --d3 workspace/pristine/FINALFANTASY7_D3.bin --in-place

    python3 mods/no-disc-swap/scripts/build_clean_d1_layer.py \
      --work path/to/ff7_d1_noswap_work.bin \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin

Expect: builder/no-disc-swap-clean-v0.1.1/layers/disc1.layer.json

    python3 -c "import json;from pathlib import Path;p=Path('builder/manifest.json');m=json.loads(p.read_text());
for a in m['addons']:
    if a.get('id')=='no-disc-swap-clean-v0.1.1': a['enabled']=True
    if a.get('id') in ('no-disc-swap-clean-v0.1.0-dev','no-disc-swap-clean-v0.1.0','no-disc-swap-clean-v0.0.0-dev'): a['enabled']=False
p.write_text(json.dumps(m,indent=2)+chr(10))"

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base clean \
      --addon no-disc-swap-clean-v0.1.1

    git add mods/no-disc-swap builder/no-disc-swap-clean-v0.1.1 builder/manifest.json
    git -c user.email=contributorindividual@gmail.com -c user.name=individualcontributordev \
      commit -m "no-disc-swap 0.1.1: release Clean D1 layer"
    git push

## Builder → burn

1. Hard refresh https://individualcontributor.dev/builder/
2. Base: Unmodified / clean
3. Add-on: No-disc-swap (Clean D1) v0.1.1
4. Disc 1 → Build → ImgBurn .cue DAO verify → console

## Evidence

    DS smoke before publish: PASS/FAIL
    verify_builder_config: PASS/FAIL
    Pushed 0.1.1 layer: yes/no
    Burn verify / console: …

Say check.

## Note

Agent clone may not have the latest work bin — layer must be built where the bin lives.
