# Task: playtest CSR + CSR+ Aerith house + Light field/world (disc 1)

## Goal

Next published-pack matrix row after Highwind Lights PASS.

## Matrix status

| Base | Field Light | World Light | Status |
|------|-------------|-------------|--------|
| Unmodified (clean) | 25 | 25 | **PASS** |
| CSR csr-v0.14.1 | on-csr-25 | on-csr-25 | **PASS** |
| Highwind highwind-v0.1.1 | on-highwind-25 | on-highwind-25 | **PASS** (script + play OK) |
| CSR + CSR+ Aerith house (D1) | on-csr-25 | on-csr-25 | **this task** |
| CSR + CSR+ Hojo (D2) | optional | optional | after D1 scene |

Verifier stacking: docs/findings/2026-07-30-verify-built-disc-stacking.md
Script now **infers** disc/base/addons from the builder folder/bin name + APPLIED.txt.

## Success

1. Builder: base **CSR**, check **CSR+ Aerith house**, Field/World **Light** (CSR variants).
2. verify_built_disc.py on the extract folder or .bin -> **PASS** (no need to type pack ids).
3. DuckStation disc 1: boots; field + world Light feel OK (one-line note). Aerith house if you reach it.

## Steps

1. git pull --ff-only in Final-Fantasy-7-Modding.
2. https://individualcontributor.dev/builder/ (hard refresh).
3. Load pristine NTSC-U **Disc 1**.
4. Base **CSR**; CSR+ Aerith house; Field Light; World Light (CSR packs).
5. Build -> extract. Point COPY-PASTE at the extract folder or .bin.
6. Paste stdout + playtest line under Evidence. Commit + push. Say **check**.

## Copy-paste

    cd "$(git rev-parse --show-toplevel)"
    git pull --ff-only

    # Folder from the builder zip (keeps APPLIED.txt next to the .bin) - preferred:
    BUILT="/c/path/to/ff7-builder-d1+csr-v0.14.1+..."

    python scripts/verify_built_disc.py "$BUILT"

Optional overrides still work: --disc / --base / --addon (must match the zip).

## Evidence

    (paste verify stdout + playtest one-liner)
