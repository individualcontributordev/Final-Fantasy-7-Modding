# Task: playtest CSR + CSR+ Aerith house + Light field/world (disc 1)

## Goal

Next published-pack matrix row after Highwind Lights PASS.

## Matrix status

| Base | Field Light | World Light | Status |
|------|-------------|-------------|--------|
| Unmodified (clean) | 25 | 25 | **PASS** |
| CSR `csr-v0.14.1` | on-csr-25 | on-csr-25 | **PASS** |
| Highwind `highwind-v0.1.1` | on-highwind-25 | on-highwind-25 | **PASS** (script + play OK) |
| CSR + CSR+ Aerith house (D1) | on-csr-25 | on-csr-25 | **this task** |
| CSR + CSR+ Hojo (D2) | optional | optional | after D1 scene |

Verifier stacking notes are journaled: `docs/findings/2026-07-30-verify-built-disc-stacking.md`.

## Success

1. Builder: base **CSR**, check **CSR+ Aerith's house**, Field Random Encounters **Light**, World Random Encounters **Light** (CSR variants).
2. `verify_built_disc.py` → **PASS** (copy-paste; includes scene addon id).
3. DuckStation disc 1: boots CSR; Aerith house scene OK if you reach it; field + world Light feel OK (one-line note).

## Steps

1. `git pull --ff-only` in Final-Fantasy-7-Modding (and CSR if scene pack missing locally).
2. https://individualcontributor.dev/builder/ (hard refresh).
3. Load pristine NTSC-U **Disc 1**.
4. Base: **CSR**. Check **CSR+ Aerith's house**. Add-ons: Field **Light**, World **Light** for CSR (not clean/Highwind packs).
5. Build → extract. Set BUILT_D1.
6. Run copy-paste. Paste stdout + playtest line under Evidence.
7. Commit this file + push. Say **check**.

## Copy-paste

    cd "$(git rev-parse --show-toplevel)"
    git pull --ff-only

    BUILT_D1="/c/path/to/builder-output/your-d1.bin"

    python scripts/verify_built_disc.py "$BUILT_D1" \
      --disc 1 \
      --base csr-v0.14.1 \
      --addon csr-plus-scene-aerith-house-v0.1.0 \
      --addon field-encounter-on-csr-25-v0.1.2 \
      --addon world-encounter-on-csr-25-v0.1.0

Use pack ids from the zip folder / APPLIED.txt if versions differ. Do not use clean or Highwind encounter ids on a CSR zip.

## Evidence

    (paste verify stdout + playtest one-liner)
