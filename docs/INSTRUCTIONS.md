# Task: Publish no-disc-swap 0.1.0-dev (movie trims) to builder + burn

## Status

- DuckStation: movie Set+Play trims working (operator)
- This agent clone does **not** have your edited work bin — build layer on the PC that has it
- Pack id after rebuild: **no-disc-swap-clean-v0.1.0-dev** (VERSION bumped)

## On the PC with the combined work bin

Work bin must include:

1. Makou Ask-for-disc removal
2. Makou Set next movie + Play movie trims (Tier 1 + descent + crawl sites)
3. SNOVA inject v3 (BATTLE.X 17 LBA remap)

If SNOVA not on that bin yet:

    python3 mods/no-disc-swap/scripts/inject_snova_d3_to_d1.py \
      --d1 path/to/ff7_d1_noswap_work.bin \
      --d3 workspace/pristine/FINALFANTASY7_D3.bin \
      --in-place

### 1. Pull + build layer

    cd Final-Fantasy-7-Modding
    git pull --ff-only

    python3 mods/no-disc-swap/scripts/build_clean_d1_layer.py \
      --work "D:\Downloads\ff7-builder-d1+clean+no-disc-swap-clean-v0.0.0-dev (1)\ff7-builder-d1+clean+no-disc-swap-clean-v0.0.0-dev.bin" \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin

Expect pack dir builder/no-disc-swap-clean-v0.1.0-dev/ and manifest entry.

### 2. Enable pack

    python3 -c "import json;from pathlib import Path;p=Path('builder/manifest.json');m=json.loads(p.read_text());
[a.__setitem__('enabled', True) for a in m['addons'] if a.get('id')=='no-disc-swap-clean-v0.1.0-dev'];
p.write_text(json.dumps(m,indent=2)+chr(10))"

Optional: set enabled false on old no-disc-swap-clean-v0.0.0-dev to avoid two choices.

### 3. Verify

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base clean \
      --addon no-disc-swap-clean-v0.1.0-dev

Must print PASS.

### 4. Commit + push (CDN)

    git add mods/no-disc-swap builder/no-disc-swap-clean-v0.1.0-dev builder/manifest.json
    git status -sb
    git -c user.email=contributorindividual@gmail.com -c user.name=individualcontributordev \
      commit -m "no-disc-swap 0.1.0-dev: FIELD movie trims + rebuild Clean D1 layer"
    git push

Wait ~1-2 min for Pages.

### 5. Builder → burn

1. https://individualcontributor.dev/builder/ (hard refresh)
2. Base: Unmodified / clean
3. Add-on: No-disc-swap Clean D1 v0.1.0-dev
4. Disc 1 → Build → zip
5. ImgBurn from .cue, DAO, 4x, verify
6. Console continue playtest

## Evidence

    Work bin has Ask+movie trims+SNOVA: yes/no
    verify_builder_config: PASS/FAIL
    Pushed: yes/no
    Builder build: PASS/FAIL
    ImgBurn verify: PASS/FAIL/not yet

Say check.

## Notes

- Do not commit .bin images
- Grown image is normal (~748.8 MB); site EDC repair supports growth
