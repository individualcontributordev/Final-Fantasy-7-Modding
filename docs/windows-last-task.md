# Task: playtest Highwind + Light field + Light world (disc 1)

## Goal

Continue published-pack matrix.

## Matrix status

| Base | Field Light | World Light | Status |
|------|-------------|-------------|--------|
| Unmodified (clean) | 25 | 25 | **PASS** |
| CSR `csr-v0.14.1` | on-csr-25 | on-csr-25 | **PASS** (human confirmed) |
| Highwind `highwind-v0.1.1` | on-highwind-25 | on-highwind-25 | **this task** |
| CSR + CSR+ scene add-ons | Aerith (D1) / Hojo (D2) | optional Lights | after Highwind |

UI check (optional glance): dropdown labels should read **Field Random Encounters** / **World Random Encounters** (smaller group font). Not a blocker for this pack test.

## Success

1. Builder: base **Highwind**, Field Random Encounters **Light**, World Random Encounters **Light** (Highwind variants only).
2. `verify_built_disc.py` → **PASS** (config below).
3. DuckStation disc 1: boots on Highwind; field + world Light feel OK (one-line note).

## Steps

1. `git pull --ff-only` in Final-Fantasy-7-Modding.
2. https://individualcontributor.dev/builder/ (hard refresh if labels look old).
3. Load pristine NTSC-U **Disc 1**.
4. Base: **Highwind**. Add-ons: Field **Light**, World **Light** for Highwind (not clean/CSR packs).
5. Build → extract. Set BUILT_D1.
6. Run copy-paste. Paste stdout + playtest line under Evidence.
7. Commit this file + push. Say **check**.

## Copy-paste

    cd "$(git rev-parse --show-toplevel)"
    git pull --ff-only

    BUILT_D1="/c/path/to/builder-output/your-d1.bin"

    python scripts/verify_built_disc.py "$BUILT_D1" \
      --disc 1 \
      --base highwind-v0.1.1 \
      --addon field-encounter-on-highwind-25-v0.1.2 \
      --addon world-encounter-on-highwind-25-v0.1.0

## Evidence

    (paste verify stdout + playtest one-liner)
 Final-Fantasy-7-Modding git:(main) ✗ python scripts/verify_built_disc.py ../../Downloads/ff7-builder-d1+highwind-v0.1.1+field-encounter-on-highwind-25-v0.1.2+world-encounter-on-highwind-25-v0.1.0/ff7-builder-d1+highwind-v0.1.1+field-encounter-on-highwind-25-v0.1.2+world-encounter-on-highwind-25-v0.1.0.bin \
  --disc 1 \
  --base highwind-v0.1.1 \
  --addon field-encounter-25-v0.1.2 \
  --addon world-encounter-25-v0.1.0
Image: D:\Downloads\ff7-builder-d1+highwind-v0.1.1+field-encounter-on-highwind-25-v0.1.2+world-encounter-on-highwind-25-v0.1.0\ff7-builder-d1+highwind-v0.1.1+field-encounter-on-highwind-25-v0.1.2+world-encounter-on-highwind-25-v0.1.0.bin (747435024 bytes)
Config: base=highwind-v0.1.1 addons=['field-encounter-25-v0.1.2', 'world-encounter-25-v0.1.0'] disc=1

=== APPLIED.txt (D:\Downloads\ff7-builder-d1+highwind-v0.1.1+field-encounter-on-highwind-25-v0.1.2+world-encounter-on-highwind-25-v0.1.0\APPLIED.txt) ===
Final Fantasy VII — IndividualContributor

Disc: 1
Base: Highwind v0.1.1
Add-ons:
  - Field Random Encounters — Light (25%) (on Highwind) v0.1.2
  - World Random Encounters — Light (25%) (on Highwind) v0.1.0
EDC/ECC sectors repaired: 4531

Play:
- Keep the .bin and .cue in the same folder.
- Open the .cue in DuckStation (or your emulator).
- Real PS2 (MechaPwn): burn from the .cue as MODE2/2352 DAO (see Modding docs/07-hardware-burn.md).
- Builder regenerates Mode2 Form1 EDC/ECC on patched sectors after applying layers.

https://individualcontributor.dev/builder/

  expect mention of 'highwind-v0.1.1': yes
  expect mention of 'field-encounter-25-v0.1.2': yes
  expect mention of 'world-encounter-25-v0.1.0': yes

=== Layer records on image ===
  base highwind-v0.1.1: 94714 records — MISSING payload @ 0x161138
  addon field-encounter-25-v0.1.2: compatibleBases=['clean'] excludes 'highwind-v0.1.1' — FAIL
  addon world-encounter-25-v0.1.0: compatibleBases=['clean'] excludes 'highwind-v0.1.1' — FAIL

=== Engine stubs (when encounter addons selected) ===
  FIELD/FIELD.BIN: stub@0xbb7c=YES
  WORLD/WORLD.BIN: stub@0x17db4=YES

Stack checked: base:highwind-v0.1.1
FAIL — built disc does not match this builder config