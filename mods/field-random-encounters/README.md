# Field random encounters

RCnt2 FORCE stub in `FIELD/FIELD.BIN` — Light / Standard / Dense field battle density.

**Play:** https://individualcontributor.dev/builder/ (add-on under the chosen cutscene base)

## Build (Windows Git Bash)

```bash
cd /c/path/to/Final-Fantasy-7-Modding
git pull

# bump VERSION first when releasing
python mods/field-random-encounters/scripts/build_all_rates.py

git add builder/
git commit -m "Field encounters vX.Y.Z — 25/50/75% for clean + CSR bases."
git push
```

One pack:

```bash
python mods/field-random-encounters/scripts/build_on_base.py --against csr-plus --rate 25 --discs 1
```

Needs `workspace/pristine/FINALFANTASY7_D1.bin`. Version: `VERSION` in this folder.

## Layout

| Path | Role |
|------|------|
| `VERSION` | Pack version string |
| `patches/` | Stub `.hex` bytes |
| `scripts/` | Build entrypoints |
| `../../builder/field-encounter-*-v*/` | Published layers (Pages) |

Shared ISO helpers: repo `scripts/` (`bin_diff_to_layer`, `psx_mode2_iso`, gzip tools).

Stub notes: [patches/README.md](patches/README.md)
