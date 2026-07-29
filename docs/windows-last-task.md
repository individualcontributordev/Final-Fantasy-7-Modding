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
```
