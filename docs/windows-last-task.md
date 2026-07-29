# Task: verify the builder zip you boot in DuckStation

## Goal

Check the **extracted builder zip** Disc 1 image (the .bin next to the .cue DuckStation opens) — not pristine. Confirm APPLIED.txt lists Unmodified/clean + Light field + Light world, and that FIELD/WORLD carry the RCnt2 FORCE stubs.

Prior **builder config** verify already PASSed on pack layers alone. This checks the **actual bootable build**.

## Prior evidence (config verify)

```
PASS — builder config applies cleanly (654 total records)
base=clean + field-encounter-25-v0.1.2 + world-encounter-25-v0.1.0 disc 1
```

## Steps

1. git pull --ff-only in **Final-Fantasy-7-Modding**.
2. Set BUILT_D1 to the Disc 1 .bin inside your **builder output folder** (same folder as the .cue you open in DuckStation).
3. Run the copy-paste block.
4. Paste full stdout under Evidence. Commit this file + push. Say **check**.

## Success looks like

- APPLIED.txt mentions field-encounter Light (25 / light) and world-encounter light (pack ids containing 25).
- FIELD/FIELD.BIN: stub@0xbb7c=YES
- WORLD/WORLD.BIN: stub@0x17db4=YES

If stubs are NO, that boot image does not have the mods — rebuild from the site builder (Unmodified + Light field + Light world), extract again, re-run.

## Copy-paste

Git Bash — edit only the BUILT_D1= path.

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only

# >>> path to the Disc 1 .bin DuckStation uses (builder zip extract) <<<
BUILT_D1="/c/path/to/builder-output/FINALFANTASY7_D1.bin"

python scripts/verify_built_disc.py "$BUILT_D1"

# if APPLIED was not found next to the bin:
# cat "$(dirname "$BUILT_D1")/APPLIED.txt"
```

## Evidence

```
```
