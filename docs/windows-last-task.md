# Task: verify the builder zip you boot in DuckStation

## Goal

Check the **extracted builder zip** Disc 1 image against the same **base + addon** config you chose in the builder (Unmodified + Light field + Light world).

Uses verify_built_disc.py with --base / --addon / --disc (same idea as verify_builder_config.py), plus APPLIED.txt + RCnt2 stubs.

Prior **builder config** verify (layers only) already PASSed.

## Steps

1. git pull --ff-only in **Final-Fantasy-7-Modding**.
2. Set BUILT_D1 to the Disc 1 .bin next to the .cue DuckStation opens.
3. Run the copy-paste block (edit pack ids only if your manifest versions differ).
4. Paste full stdout under Evidence. Commit this file + push. Say **check**.

## Success looks like

- Final line: PASS — built disc matches base+addon config
- Layer records OK for each addon
- FIELD stub@0xbb7c=YES and WORLD stub@0x17db4=YES

## Copy-paste

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only

# >>> path to the Disc 1 .bin DuckStation uses (builder zip extract) <<<
BUILT_D1="/c/path/to/builder-output/FINALFANTASY7_D1.bin"

python scripts/verify_built_disc.py "$BUILT_D1" \
  --disc 1 \
  --base clean \
  --addon field-encounter-25-v0.1.2 \
  --addon world-encounter-25-v0.1.0
```

## Evidence

```
7-Modding git:(main) python scripts/verify_built_disc.py ../../Downloads/ff7-builder-d1+clean+field-encounter-25-v0.1.2+world-encounter-25-v0.1.0/ff7-builder-d1+clean+field-encounter-25-v0.1.2+world-encounter-25-v0.1.0.bin \
  --disc 1 \
  --base clean \
  --addon field-encounter-25-v0.1.2 \
  --addon world-encounter-25-v0.1.0
Image: D:\Downloads\ff7-builder-d1+clean+field-encounter-25-v0.1.2+world-encounter-25-v0.1.0\ff7-builder-d1+clean+field-encounter-25-v0.1.2+world-encounter-25-v0.1.0.bin (747435024 bytes)
Config: base=clean addons=['field-encounter-25-v0.1.2', 'world-encounter-25-v0.1.0'] disc=1

=== APPLIED.txt (D:\Downloads\ff7-builder-d1+clean+field-encounter-25-v0.1.2+world-encounter-25-v0.1.0\APPLIED.txt) ===
Final Fantasy VII — IndividualContributor

Disc: 1
Base: Unmodified (retail)
Add-ons:
  - Field encounters — Light (25%) v0.1.2
  - World encounters — Light (25%) v0.1.0
EDC/ECC sectors repaired: 75

Play:
- Keep the .bin and .cue in the same folder.
- Open the .cue in DuckStation (or your emulator).
- Real PS2 (MechaPwn): burn from the .cue as MODE2/2352 DAO (see Modding docs/07-hardware-burn.md).
- Builder regenerates Mode2 Form1 EDC/ECC on patched sectors after applying layers.

https://individualcontributor.dev/builder/

  expect mention of 'clean': yes
  expect mention of 'field-encounter-25-v0.1.2': yes
  expect mention of 'world-encounter-25-v0.1.0': yes

=== Layer records on image ===
  base clean: (no base layer)
  addon field-encounter-25-v0.1.2: 364 records — OK
  addon world-encounter-25-v0.1.0: 290 records — OK

=== Engine stubs (when encounter addons selected) ===
  FIELD/FIELD.BIN: stub@0xbb7c=YES
  WORLD/WORLD.BIN: stub@0x17db4=YES

Stack checked: base:clean, addon:field-encounter-25-v0.1.2, addon:world-encounter-25-v0.1.0
PASS — built disc matches base+addon config (layer payloads present)
➜  Final-Fantasy-7-Modding git:(main)

g_danger 2 bytes 
["duckstation-qt-x64-ReleaseLTCG.exe"+7F1600]+7173C

g_world_danger
["duckstation-qt-x64-ReleaseLTCG.exe"+7F1600]+116284
```
