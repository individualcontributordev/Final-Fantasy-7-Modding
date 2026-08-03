# Task: Publish no-disc-swap 0.1.1-dev after brief DS smoke

## VERSION

mods/no-disc-swap/VERSION = **0.1.1-dev** (bumped; layer not built on this clone).

## After your DuckStation minute

If smoke is OK, on the PC with the **combined work bin**:

    cd Final-Fantasy-7-Modding
    git pull --ff-only

Work bin must have: Ask trims + all movie Set/Play trims + SNOVA v3.

If SNOVA missing:

    python3 mods/no-disc-swap/scripts/inject_snova_d3_to_d1.py \
      --d1 path/to/work.bin \
      --d3 workspace/pristine/FINALFANTASY7_D3.bin \
      --in-place

### Build + enable + verify

    python3 mods/no-disc-swap/scripts/build_clean_d1_layer.py \
      --work path/to/work.bin \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin

    python3 -c "import json;from pathlib import Path;p=Path('builder/manifest.json');m=json.loads(p.read_text());
[a.__setitem__('enabled', True) for a in m['addons'] if a.get('id')=='no-disc-swap-clean-v0.1.1-dev'];
[a.__setitem__('enabled', False) for a in m['addons'] if a.get('id') in ('no-disc-swap-clean-v0.1.0-dev','no-disc-swap-clean-v0.0.0-dev')];
p.write_text(json.dumps(m,indent=2)+chr(10))"

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base clean \
      --addon no-disc-swap-clean-v0.1.1-dev

### Push

    git add mods/no-disc-swap builder/no-disc-swap-clean-v0.1.1-dev builder/manifest.json
    git -c user.email=contributorindividual@gmail.com -c user.name=individualcontributordev \
      commit -m "no-disc-swap 0.1.1-dev: more movie trims + Clean D1 layer"
    git push

Builder: clean + No-disc-swap v0.1.1-dev → Disc 1 → burn.

## Evidence

    DS smoke: PASS/FAIL
    Layer built/pushed: yes/no
    verify: PASS/FAIL

Say check.
