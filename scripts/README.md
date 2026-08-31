# Shared scripts (repo root `scripts/`)

Small, single-purpose tools for FF7 PSX ISO / FIELD work. **Mod build entrypoints**
live under `mods/<name>/scripts/` — not here.

Each script: one job, `--help`, docstring with when/why. Libraries have no CLI.

## When to use what

| Want | Tool | Notes |
|------|------|--------|
| **Look up field/movie/music ID** | `query_ff7_ids.py` | Canonical reference — see `docs/reference/INDEX.md` |
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
| Build BATRES s4=0 smoke image | `build_batres_s4zero_image.py` | Ceremony wait skip test disc |
| Build BATRES ceremony smokes (s4 / anim4) | `build_batres_ceremony_smoke.py` | Fanfare wait/pose experiments |
| Verify pack stack like the site | `verify_builder_config.py` | Before publish |
| Smoke a built disc image | `verify_built_disc.py` | Needs `APPLIED.txt` beside image |
| **Regression suite** | `tests/` + `pytest` | Unit (no bins) + integration (CSR stack) |
| Find opcode/byte pattern in a field script | `field_pattern_finder.py` | Tags hits `[CONFIRMED]`/`[UNCONFIRMED]` — see Verification contract; `--decode-fields` also prints each `--opcode` hit's named-field breakdown (via `opcode_struct_decoder.py`) |
| Look up a RAM address/function name | `duckstation_addr_advisor.py` | Cross-checks `docs/05-ghidra-guide.md` checklist + `scripts/ghidra/*.json` |
| Opcode struct field layouts (banks/value1/oper/jump...) | `opcode_struct_layout.py` | Library — extracted from `external/makoureactor` `Opcode.h` |
| Decode raw opcode param bytes into named fields | `opcode_struct_decoder.py` | CLI — `--list-mismatches` cross-checks vs `ff7_opcodes.py` |
| ff7-decomp + ffvii global symbol → RAM address | `decomp_symbol_map.py` | Library — `D_<hex>`/`func_<hex>`-named symbols encode their own address; merges `external/ff7-decomp` (gameplay) + `external/ffvii` (boot, tracks decompiled-vs-stub) |
| Look up decomp symbol by name/address | `decomp_symbol_lookup.py` | CLI — `--addr ... --nearest` finds containing struct/array |
| ff7-decomp struct field layouts (SaveWork, FieldEntity, ...) | `decomp_struct_layout.py` | Library — extracted from `external/ff7-decomp` headers |
| Decode raw memory dump against a decomp struct | `decomp_struct_decoder.py` | CLI — `--symbol Savemap` anchors output to absolute RAM addresses |
| World-map (`wmX.ev`) worldscript opcode layouts | `worldmap_opcode_layout.py` | Library — extracted from `external/ff7-landscaper`'s shipping TS opcode table; different VM than field opcodes (stack-based, 16-bit words) |
| Look up / decode world-map opcode ids | `worldmap_opcode_lookup.py` | CLI — `--words` decodes a raw word stream; handles `CALL_FN_0..43` (0x204-0x22F) range |
| PC-version (1998 .exe) struct field layouts | `pc_struct_layout.py` | Library — extracted from `external/ff7-chocobo`/`ff7-coaster` (`ergonomy_joe`); PC binary, not PSX — don't mix with `decomp_struct_layout.py` |
| Decode raw memory dump against a PC struct | `pc_struct_decoder.py` | CLI — `--base` prefixes output with an absolute address if you have one |

Single-disc playtest / SNOVA / movies: `mods/single-disc/scripts/` (see that mod’s README + skill `ship-single-disc`).

**New to building locally (no agent)?** Start with [docs/08-engineer-build-guide.md](../docs/08-engineer-build-guide.md).

### Regression tests (prevent single-disc / builder breakage)

```bash
# once per machine (dev dep — see requirements-dev.txt)
python3 -m pip install -r requirements-dev.txt

# Fast: apply_layer pad, builder ranks, EDC Form2 skip, prefer-list, manifest
cd Final-Fantasy-7-Modding && python3 -m pytest tests/ -q -m "not integration"

# Full stack (needs workspace/pristine + CSR cache/layers): Hojo, break,
# waterfall LBA, PARASHOT/NRCRL, MD8_5 assets, endings non-clobber
python3 -m pytest tests/ -q
# or only integration:
python3 -m pytest tests/ -q -m integration
```

Integration skips cleanly when disc images are missing. Run **full** suite before publishing a new `csr-plus`/`highwind` collapsed base.

### RAG index (semantic search over vendored RE repos + chat history)

```bash
# once per machine (separate from requirements-dev.txt -- pulls in torch)
python3 -m venv .venv_rag
.venv_rag/bin/pip install -r requirements-rag.txt

# clone/update the vendored reference repos (external/, gitignored)
bash scripts/init_external_repos.sh

# rebuild the index (rare -- only after external/ repos update or new
# source dirs are added to SOURCE_DIRS in build_rag_index.py)
source .venv_rag/bin/activate
python3 scripts/build_rag_index.py

# query the committed index (rag_index/chunks.jsonl + embeddings.npz)
python3 scripts/rag_retrieve.py "worldscript CALL_FN opcode encoding"
```

If `.venv_rag` doesn't exist in a fresh session, `rag_retrieve.py`/
`build_rag_index.py` fail on `import sentence_transformers` — run the setup
above first. The committed `rag_index/` works without rebuilding as long as
the venv exists to embed the query.

## Quick starts

```bash
# Help (every CLI)
python3 scripts/query_ff7_ids.py -h
python3 scripts/compare_field_dat.py -h
python3 scripts/extract_field_dat.py -h
python3 scripts/put_field_dat.py -h

# Look up field/movie/music IDs (see docs/reference/INDEX.md)
python3 scripts/query_ff7_ids.py field 637          # → loslake1
python3 scripts/query_ff7_ids.py movie 0x2f         # → jairofal (Disc1)
python3 scripts/query_ff7_ids.py music 82           # → One-Winged Angel

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

# Find an opcode/byte pattern in a field script (CONFIRMED/UNCONFIRMED tagged)
python3 scripts/field_pattern_finder.py pristine:1 --field LOST2 --opcode MUSIC
python3 scripts/field_pattern_finder.py csr:1 --field DEL1 --hex f052
python3 scripts/field_pattern_finder.py pristine:1 --field LOST2 --opcode MUSIC --decode-fields

# Check whether an address/function name is emulator-confirmed or just Ghidra auto-analysis
python3 scripts/duckstation_addr_advisor.py 0x800AB9C8
python3 scripts/duckstation_addr_advisor.py increment_step_id

# Decode a field-script opcode's raw param bytes into named fields
python3 scripts/opcode_struct_decoder.py IFUB 0102030405
python3 scripts/opcode_struct_decoder.py --list-mismatches

# Look up a ff7-decomp global by name/address, and decode a memory dump
# against a decomp struct (e.g. the savemap at 0x8009C6E4)
python3 scripts/decomp_symbol_lookup.py --name Savemap
python3 scripts/decomp_symbol_lookup.py --addr 0x8009D000 --nearest
python3 scripts/decomp_struct_decoder.py SaveWork <hexbytes> --symbol Savemap
python3 scripts/decomp_struct_decoder.py --list-structs

# Look up / decode world-map worldscript opcodes (wm0.ev etc.)
python3 scripts/worldmap_opcode_lookup.py --id 0x318
python3 scripts/worldmap_opcode_lookup.py --words 0318 0005 0000
python3 scripts/worldmap_opcode_lookup.py --list

# Decode a raw memory dump against a PC-version (1998 .exe) struct
python3 scripts/pc_struct_decoder.py VECTOR 01000000020000000300000004000000
python3 scripts/pc_struct_decoder.py --list-structs
```

## Design rules (agents + humans)

1. **Single responsibility** — one problem per script; share code via importable modules.
2. **Developer-friendly** — argparse `-h`, module docstring (what / when / examples), plain errors.
3. **No absolute machine paths** — resolve repos relative to this tree or env.
4. **Libraries vs CLI** — `field_dat.py` is not a CLI; `compare_field_dat.py` is.
5. **Document discovery** — new tool → row in this table + rule/skill touch if workflow changes.

CSR sibling default: `../Final-Fantasy-7-CSR` from repo root (override with env if needed).

## Verification contract: CONFIRMED vs UNCONFIRMED

RE tools that emit an address, opcode offset, or structure guess (currently
`field_pattern_finder.py`, `duckstation_addr_advisor.py`,
`opcode_struct_decoder.py`, `decomp_symbol_lookup.py`,
`decomp_struct_decoder.py`, `worldmap_opcode_lookup.py`, and
`pc_struct_decoder.py`) MUST tag every result line with one of:

- **`[CONFIRMED]`** — the value was cross-checked against a local source of
  truth: parsed directly from the target file via `field_dat.py`/
  `ff7_opcodes.py` (ground-truth opcode tables), or matched against an
  entry in the `docs/05-ghidra-guide.md` "Functions to identify" checklist
  (the `- [x]` lines), which represents emulator-correlated addresses.
- **`[UNCONFIRMED: <reason>]`** — anything else, e.g. a heuristic match from
  Ghidra auto-analysis (`scripts/ghidra/field-functions.json`,
  `field-symbols.json`) that has no checklist entry or emulator
  correlation, a pattern match with no cross-reference, or a guess derived
  by proximity/naming only. `<reason>` states *why* it isn't confirmed
  (e.g. `no checklist entry`, `auto-analysis only, no emulator correlation`).

Never print a bare address/offset without one of these tags — this is what
lets an agent tell "verified fact" from "still needs a live DuckStation
correlation pass" without re-deriving it each time.
