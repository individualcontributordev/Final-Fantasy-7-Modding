# INSTRUCTIONS — run single-disc regression tests (machine with bins)

## Why

Confirms the published CSR + movies + single-disc stack still holds prior fixes
(PARASHOT, Hojo, break, waterfall, MD8, apply order). Needs disc images on this PC.

## One-time setup (if pytest missing)

Open Terminal / Git Bash in the Modding repo, then COPY-PASTE:

    cd ~/Final-Fantasy-7-Modding
    git pull --ff-only
    python3 -m pip install -r requirements-dev.txt

(Adjust cd if your clone path differs.)

## Run all tests

    cd ~/Final-Fantasy-7-Modding
    git pull --ff-only
    python3 -m pytest tests/ -q

## Run integration only

    cd ~/Final-Fantasy-7-Modding
    python3 -m pytest tests/ -q -m integration

## What you need on this machine

| Path | Role |
|------|------|
| workspace/pristine/FINALFANTASY7_D1.bin | Pristine Disc 1 |
| workspace/pristine/FINALFANTASY7_D2.bin | Pristine Disc 2 (path FMV sources) |
| Sibling ../Final-Fantasy-7-CSR/cache/csr/FINALFANTASY7_D1.bin (and D2) | Preferred CSR images; or CSR layers + pristine |
| builder/single-disc-on-csr-v0.1.24/ + movies pack | Published layers (from git pull) |

If bins are missing, integration tests skip; unit tests still run.

## Success

- Last line like: 22 passed (or 9 passed for integration-only)
- Exit code 0 — no FAILED lines

## Evidence (paste in chat or below)

EXIT CODE:

(pytest full output, or at least the summary line)

## After tests pass — still build a playtest bin for PARASHOT in DuckStation

1. Hard-refresh https://individualcontributor.dev/builder/
2. Base CSR + Single-disc v0.1.24 (CSR+ off for this check)
3. APPLIED should list manip-movies v0.1.4 and single-disc-on-csr-v0.1.24
4. Build Disc 1; test Highwind deck FSHIP_12 for full PARASHOT

Optional override if CSR lives elsewhere:

    export FF7_CSR_ROOT=/path/to/Final-Fantasy-7-CSR
    export FF7_PRISTINE_DIR=/path/to/pristine
    python3 -m pytest tests/ -q
