# Task: verify Unmodified + Light field/world as a builder config

## Goal

Confirm the same stack the **site builder** would apply for **Unmodified + Light field + Light world** on Disc 1 stacks cleanly from `builder/` packs (no zip path / env vars required beyond pristine).

## Steps

1. `git pull --ff-only` in **Final-Fantasy-7-Modding**.
2. **Final-Fantasy-7-CSR** should sit as a sibling clone (wrapper default), or pass `--csr-root`.
3. Point `--pristine` at a retail Disc 1 `.bin` (this repo `workspace/pristine/` or CSR’s).
4. Run the copy-paste block. Edit pack ids only if `builder/manifest.json` shows newer versions.
5. Paste full stdout under [Evidence](#evidence). One line on prior DuckStation Danger feel is fine. Commit this file + push. Say **check**.

## Success looks like

- Line: `PASS — builder config applies cleanly`
- Addons resolve: `field-encounter-25-v0.1.2`, `world-encounter-25-v0.1.0` on base `clean`

## Copy-paste

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only

# Prefer local pristine; fallback to CSR sibling if needed
if [ -f workspace/pristine/FINALFANTASY7_D1.bin ]; then
  PRISTINE="workspace/pristine/FINALFANTASY7_D1.bin"
else
  PRISTINE="../Final-Fantasy-7-CSR/workspace/pristine/FINALFANTASY7_D1.bin"
fi

python scripts/verify_builder_config.py \
  --pristine "$PRISTINE" \
  --disc 1 \
  --base clean \
  --addon field-encounter-25-v0.1.2 \
  --addon world-encounter-25-v0.1.0
```

## Evidence

```
```
