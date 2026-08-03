# Task: Publish No-disc-swap Clean D1 pack (other PC)

## Rename

Mod path is now: mods/no-disc-swap/
Pack id: no-disc-swap-clean-v0.0.0-dev
Manifest: enabled false until you flip it after layer rebuild.

## Why rebuild on the other PC

This machine layer may be SNOVA-only. The burn pack must come from your
combined work bin (Makou Ask removal + SNOVA inject v3).

## On the publish/build PC

### 0. Pull

    cd Final-Fantasy-7-Modding
    git pull --ff-only

Need:
- workspace/pristine/FINALFANTASY7_D1.bin
- workspace/pristine/FINALFANTASY7_D3.bin
- Your combined Ask+SNOVA image (or rebuild below)

### 1. Rebuild combined work bin (if needed)

Recipe: mods/no-disc-swap/README.md

    cp -f workspace/pristine/FINALFANTASY7_D1.bin workspace/iso-extract/ff7_d1_noswap_work.bin
    # Makou: remove all Ask-for-disc; save into work bin
    cp -f workspace/iso-extract/ff7_d1_noswap_work.bin workspace/iso-extract/ff7_d1_noswap_work.pre_snova.bak
    python3 mods/no-disc-swap/scripts/inject_snova_d3_to_d1.py \
      --d1 workspace/iso-extract/ff7_d1_noswap_work.bin \
      --d3 workspace/pristine/FINALFANTASY7_D3.bin \
      --in-place

Must see: BATTLE.X LBA patch v3 and 17 LBA entries remapped.

### 2. Build builder layer + flip enable

    python3 mods/no-disc-swap/scripts/build_clean_d1_layer.py \
      --work workspace/iso-extract/ff7_d1_noswap_work.bin \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin

Edit builder/manifest.json for id no-disc-swap-clean-v0.0.0-dev:
set "enabled": true

Or one-liner:

    python3 -c "import json;from pathlib import Path;p=Path('builder/manifest.json');m=json.loads(p.read_text());[a.__setitem__('enabled', True) for a in m['addons'] if a.get('id')=='no-disc-swap-clean-v0.0.0-dev'];p.write_text(json.dumps(m,indent=2)+chr(10))"

### 3. Verify (required)

    python3 scripts/verify_builder_config.py \
      --pristine workspace/pristine/FINALFANTASY7_D1.bin \
      --disc 1 --base clean \
      --addon no-disc-swap-clean-v0.0.0-dev

Must print PASS.

### 4. Commit + push (publishes GitHub Pages CDN)

    git add mods/no-disc-swap builder/no-disc-swap-clean-v0.0.0-dev builder/manifest.json
    git status -sb
    git -c user.email=contributorindividual@gmail.com -c user.name=individualcontributordev commit -m "no-disc-swap: publish Clean D1 pack for console burn"
    git push

Wait for Pages deploy (usually 1-2 min).

### 5. Builder on burn PC

1. Open https://individualcontributor.dev/builder/
2. Hard refresh if old list cached
3. Base: Unmodified / clean
4. Add-on: No-disc-swap — Clean D1 …
5. Disc 1 only
6. Build → download .bin
7. Before optical burn: repair Mode2 EDC/ECC (docs/07-hardware-burn.md)
8. Console smoke: new game, disc-ask skip, Supernova if possible

## Evidence

    Layer rebuilt from combined: yes/no
    verify_builder_config: PASS/FAIL
    Pack enabled + pushed: yes/no
    Builder download OK: yes/no
    Burn/EDC notes:
    Console: …

Say check.

## Notes

- Do not commit .bin images
- Pack is D1-only; D2/D3 layers not required for this add-on
- Leave CSR movie copies out for now (wrong FMV wait finding)

If $GameMoment == 1398 (else goto label 1)
	Execute script #3 in group Untitled (No5) (priority 6/6) - Waiting for end of execution to continue
	Wait 3 frame
	Set next movie: No57 (disc 1), loslake1 (disc 2), No57 (disc 3)
	Execute script #4 in extern group mf (No1) (priority 6/6) - Only if the script is not already running
	Play movie
	Execute script #6 in extern group Untitled (No6) (priority 6/6) - Only if the script is not already running
	Execute script #6 in group Untitled (No5) (priority 6/6) - Waiting for end of execution to continue
	Set next movie: No58 (disc 1), lslmv (disc 2), No58 (disc 3)
	Execute script #3 in extern group mf (No1) (priority 6/6) - Only if the script is not already running
	Play movie
	Wait 10 frame
	Execute script #7 in group Untitled (No5) (priority 6/6) - Waiting for end of execution to continue
	Wait 20 frame
	Jump to map loslake1 (#637) (X=643, Y=-324, triangle ID=19, direction=176)
Label 1
Goto label 1
