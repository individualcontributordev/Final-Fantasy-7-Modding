# Shared scripts (repo root `scripts/`)

Small, single-purpose tools for FF7 PSX ISO / FIELD work. **Mod build entrypoints**
live under `mods/<name>/scripts/` — not here.

Each script: one job, `--help`, docstring with when/why. Libraries have no CLI.

## When to use what

| Want | Tool | Notes |
|------|------|--------|
| Compare two field maps (opcodes, pad vs text) | `compare_field_dat.py` | Prefer over byte-size / compressed diffs |
| Extract one `FIELD/*.DAT` from pristine/CSR/bin | `extract_field_dat.py` | Read-only |
| Write one `FIELD/*.DAT` into a work `.bin` | `put_field_dat.py` | Padded slot; refuses longer |
| Pristine/CSR path resolution | `disc_sources.py` | Library only |
| Apply builder layer to a `.bin` | `apply_layer.py` | `ic-layer-v1` only |
| Diff two bins → layer JSON | `bin_diff_to_layer.py` | Publish path |
| Read/write ISO file extents | `psx_mode2_iso.py` | Library |
| LZS decompress FIELD `.DAT` | `lzs.py` | Library |
| Parse field DAT sections/scripts | `field_dat.py` | Library |
| Structured field diff objects | `field_compare.py` | Library |
| Opcode names/sizes | `ff7_opcodes.py` | Library (Makou table) |
| GZIPPS FIELD.BIN / WORLD.BIN / **BATTLE/*.X** | `decompress_gzipps.py` / `compress_gzipps.py` | Engine overlays; Ghidra: [docs/ghidra-battle-overlays.md](../docs/ghidra-battle-overlays.md) |
| Verify pack stack like the site | `verify_builder_config.py` | Before publish |
| Smoke a built disc image | `verify_built_disc.py` | Needs `APPLIED.txt` beside image |

Single-disc playtest / SNOVA / movies: `mods/single-disc/scripts/` (see that mod’s README + skill `ship-single-disc`).

## Quick starts

```bash
# Help (every CLI)
python3 scripts/compare_field_dat.py -h
python3 scripts/extract_field_dat.py -h
python3 scripts/put_field_dat.py -h

# CSR Disc 1 vs Disc 2 for one map
python3 scripts/compare_field_dat.py csr:1 csr:2 --field DEL1 -o /tmp/del1.md

# All known multi-disc CSR field collisions
python3 scripts/compare_field_dat.py --batch-collisions

# Pull CSR Disc 1 DEL1, put onto a work image
python3 scripts/extract_field_dat.py --from csr:1 --field DEL1 \
  -o workspace/iso-extract/field-merge/DEL1_csr_d1.DAT
python3 scripts/put_field_dat.py --bin workspace/iso-extract/work.bin \
  --field DEL1 --dat workspace/iso-extract/field-merge/DEL1_csr_d1.DAT

# Pristine + layer → work bin
python3 scripts/apply_layer.py workspace/pristine/FINALFANTASY7_D1.bin \
  ../Final-Fantasy-7-CSR/builder/csr-v0.14.1/layers/disc1.layer.json \
  -o workspace/iso-extract/out.bin
```

## Design rules (agents + humans)

1. **Single responsibility** — one problem per script; share code via importable modules.
2. **Developer-friendly** — argparse `-h`, module docstring (what / when / examples), plain errors.
3. **No absolute machine paths** — resolve repos relative to this tree or env.
4. **Libraries vs CLI** — `field_dat.py` is not a CLI; `compare_field_dat.py` is.
5. **Document discovery** — new tool → row in this table + rule/skill touch if workflow changes.

CSR sibling default: `../Final-Fantasy-7-CSR` from repo root (override with env if needed).
