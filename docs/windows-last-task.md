# Task: playtest CSR base + Light field + Light world (disc 1)

## Goal

Continue published-pack matrix. **Already done:** Unmodified (clean) + Light field + Light world — builder zip PASS, runtime field OK, world FORCE 0/FFFF + battle confirmed.

**This task:** same encounter Lights on **CSR** base (not clean, not Highwind yet).

## Matrix status

| Base | Field Light | World Light | Status |
|------|-------------|-------------|--------|
| Unmodified (clean) | 25 | 25 | **PASS** (prior session) |
| CSR `csr-v0.14.1` | on-csr-25 | on-csr-25 | **this task** |
| Highwind `highwind-v0.1.1` | on-highwind-25 | on-highwind-25 | later |
| CSR + CSR+ scene checkboxes | — | — | later |

## Success

1. Browser builder: base **CSR**, Field encounters **Light**, World encounters **Light** (on-csr packs). Build disc 1 zip.
2. `verify_built_disc.py` → **PASS** for the config below.
3. DuckStation: boots; field feels Light; world map still gets occasional battles (stub live). Optional: one line that both feel OK.

## Steps

1. `git pull --ff-only` in Final-Fantasy-7-Modding (and CSR sibling if used for pristine/tools).
2. https://individualcontributor.dev/builder/ — hard refresh if needed.
3. Load pristine NTSC-U **Disc 1**.
4. Base: **CSR**. Add-ons: Field **Light**, World **Light** (must be the CSR-compatible variants, not clean-only).
5. Build → extract zip. Note folder path for BUILT_D1.
6. Run copy-paste verify. Paste full stdout under Evidence.
7. Short DuckStation play (field + world grass). One-line playtest note under Evidence.
8. Commit this file + push. Say **check**.

## Copy-paste

Git Bash — set BUILT_D1 to the built disc 1 .bin:

    cd "$(git rev-parse --show-toplevel)"
    git pull --ff-only

    BUILT_D1="/c/path/to/builder-output/your-d1.bin"

    python scripts/verify_built_disc.py "$BUILT_D1" \
      --disc 1 \
      --base csr-v0.14.1 \
      --addon field-encounter-on-csr-25-v0.1.2 \
      --addon world-encounter-on-csr-25-v0.1.0

## Evidence

    (paste verify stdout + playtest one-liner)
