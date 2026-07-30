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
