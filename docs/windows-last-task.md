# Task: verify Unmodified + Light field/world built disc (Danger ramp)

## Goal

Prove whether the DuckStation Disc 1 image you boot actually has the Light field (and world) RCnt2 FORCE stubs applied. Vanilla Danger that climbs steadily usually means the FIELD stub is **not** present (wrong image, or pack not in `APPLIED.txt`).

## Steps

1. `git pull --ff-only` in **Final-Fantasy-7-Modding** (this repo).
2. Set `BUILT_D1` to the Disc 1 `.bin` next to the `.cue` DuckStation opens (builder zip extract folder — **not** pristine redump).
3. Run `verify_built_disc.py` on that path (commands below).
4. Paste full script stdout under [Evidence](#evidence) (and `APPLIED.txt` text if the script did not find it).
5. Commit this file + push. Say **check**.

## Success looks like

- `APPLIED.txt` mentions field-encounter Light (`25` / light) on clean, and world-encounter light if you selected it.
- `FIELD/FIELD.BIN` line: `stub@0xbb7c=YES`
- `WORLD/WORLD.BIN` line: `stub@0x17db4=YES` (if world light was selected)

If `FIELD stub@0xbb7c=NO` → pack not on that image; rebuild Unmodified + Light with the **clean** `field-encounter-25` pack and re-verify before more DuckStation time.

## Copy-paste

Git Bash — edit **only** the `BUILT_D1=` path.

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only

# >>> set this to your built Disc 1 .bin (DuckStation's folder) <<<
BUILT_D1="/c/path/to/builder-output/FINALFANTASY7_D1.bin"

python scripts/verify_built_disc.py "$BUILT_D1"

# optional: show APPLIED next to bin if verify said not found
# cat "$(dirname "$BUILT_D1")/APPLIED.txt"
```

## Evidence

Paste script output below, then save.

```
```
