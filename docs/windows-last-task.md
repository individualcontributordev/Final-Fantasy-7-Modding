# Task: pull CSR then re-run Unmodified + Light config verify

## Goal

Last run failed because **Final-Fantasy-7-CSR** on Windows lacked
`scripts/verify_builder_config.py` (clone behind `main`). Pull CSR, then re-run the clean + Light field/world stack verify.

## Prior evidence (keep for history)

```
CSR verify script not found: D:\projects\Final-Fantasy-7-CSR\scripts\verify_builder_config.py
```

## Steps

1. Pull **both** repos (CSR first).
2. Confirm the CSR script exists.
3. Re-run `verify_builder_config.py` for clean + Light field + Light world, disc 1.
4. Paste full stdout under [Evidence](#evidence). One line on prior DuckStation Danger feel is fine. Commit this file + push. Say **check**.

## Success looks like

- `ls` / `test -f` shows CSR `scripts/verify_builder_config.py`
- Final line: `PASS — builder config applies cleanly`

## Copy-paste

```bash
# 1) CSR must be current
cd /d/projects/Final-Fantasy-7-CSR
git pull --ff-only
test -f scripts/verify_builder_config.py && echo "CSR script OK" || echo "CSR script MISSING"

# 2) Modding + verify
cd /d/projects/Final-Fantasy-7-Modding
git pull --ff-only

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

If your CSR path is not `D:\projects\Final-Fantasy-7-CSR`, fix the `cd` paths or:

```bash
python scripts/verify_builder_config.py \
  --csr-root "/d/path/to/Final-Fantasy-7-CSR" \
  --pristine "$PRISTINE" \
  --disc 1 --base clean \
  --addon field-encounter-25-v0.1.2 \
  --addon world-encounter-25-v0.1.0
```

## Evidence

```
```
