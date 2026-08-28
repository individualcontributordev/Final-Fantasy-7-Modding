# Final Fantasy VII PSX Modding

Tools and notes for modifying **Final Fantasy VII** PlayStation disc images (hardware-compatible).

**Play:** https://individualcontributor.dev/builder/  
**Repo:** https://github.com/individualcontributordev/Final-Fantasy-7-Modding

## Mods

| Mod | Path | Builder | Changelog |
|-----|------|---------|-----------|
| Field random encounters | [mods/field-random-encounters/](mods/field-random-encounters/) | Light / Standard / Dense | [CHANGELOG](mods/field-random-encounters/CHANGELOG.md) |
| World map random encounters | [mods/world-map-random-encounters/](mods/world-map-random-encounters/) | Light / Standard / Dense | [CHANGELOG](mods/world-map-random-encounters/CHANGELOG.md) |
| Fanfare Skip | [mods/fanfare-skip/](mods/fanfare-skip/) | No victory song/poses (train-style) | [CHANGELOG](mods/fanfare-skip/CHANGELOG.md) |

Release notes index: **[CHANGELOGS.md](CHANGELOGS.md)** (newest entry at the **top** of each file).

## Layout

```
mods/<name>/          source of truth (VERSION, CHANGELOG, patches, scripts/)
mods/<name>/scripts/  that mod's build pipeline (build_all_rates, build_on_base, …)
builder/              published ic-layer-v1 packs + manifest.json (Pages CDN)
scripts/              shared only: ISO / gzip / layer / verify helpers
docs/                 RE reference + findings lab notebook
workspace/            local pristine discs / temps (gitignored)
CHANGELOGS.md         index of mod release notes (newest-at-top rule)
```

Mod build entrypoints live under `mods/<name>/scripts/`, not root `scripts/`.
Root `scripts/` is for reusable disc/ISO tools (`apply_layer`, `verify_*`, compress, …).

## Play

Use the disc builder: pick a cutscene base, optional Field encounter density, download zip.

## Release Field encounters

Needs `workspace/pristine/FINALFANTASY7_D1.bin` (never open in CDmage).

```bash
cd /c/path/to/Final-Fantasy-7-Modding
git pull

# bump mods/field-random-encounters/VERSION when shipping a new release
python mods/field-random-encounters/scripts/build_all_rates.py

git add builder/
git status   # JSON only — no .bin
git commit -m "Field encounters v0.1.2 — Light/Standard/Dense for clean + CSR bases."
git push
```

One pack (omit `--density` to pick Light / Standard / Dense / All interactively):

```bash
python mods/field-random-encounters/scripts/build_on_base.py --against csr --discs 1
# or non-interactive:
python mods/field-random-encounters/scripts/build_on_base.py --against csr --density light --discs 1
```

`--against` resolves the live CSR base id from Pages. Older packs stay enabled until you set `"enabled": false` in `builder/manifest.json`.

Densities are **named presets** (not a free-form %): **Light** / **Standard** / **Dense**. Stub notes: `mods/field-random-encounters/patches/`.

## For engineers (RE)

| Doc | Contents |
|-----|----------|
| [docs/06-new-mod-research.md](docs/06-new-mod-research.md) | Idea → RE → patch → builder pack |
| [docs/01-encounter-system.md](docs/01-encounter-system.md) | Field encounter RAM / Ghidra map |
| [docs/02-disc-format.md](docs/02-disc-format.md) | ISO, GZIPPS, Makou |
| [docs/03-environment-setup.md](docs/03-environment-setup.md) | Tools checklist |
| [docs/04-workflow.md](docs/04-workflow.md) | Edit → inject → verify |
| [docs/05-ghidra-guide.md](docs/05-ghidra-guide.md) | Ghidra workflow |
| [docs/findings/](docs/findings/) | Dated lab notebook |

After clone: `git config core.hooksPath .githooks`

## AI-assisted RE pipeline (local, optional)

Local fine-tuned-model workflow for opcode/maplist assistance. Not required for building mods.

- **Model**: DeepSeek-R1-8B + LoRA adapters (Unsloth, 4-bit) trained on `data/ff7_re_dataset.jsonl` (1,348 rows covering all 256 field opcodes and 788 maplist entries, sourced from `~/makoureactor`/`~/ff7tk`/this repo's `scripts/ff7_opcodes.py`).
- **Reference paths** (see `AGENTS.md` for full rules):
  - `~/Final-Fantasy-7-CSR` — RE notes/logs, `field_maplist.py`
  - `~/makoureactor`, `~/ff7tk` — opcode/maplist ground truth
  - `~/Downloads/ghidra_12.1.2_PUBLIC` — Ghidra
- **Run the agent**: `python3 run_ff7_agent.py` — interactive loop; requires a real LoRA checkpoint dir passed to `FastLanguageModel.from_pretrained(model_name=...)` (edit the `model_name` at the top of the script — no checkpoint ships in this repo).
- **Extract real test assets**: `python3 extract_game_assets.py` — pulls genuine `FIELD/*.DAT` files (e.g. `FSHIP_12.DAT`, `MD8_5.DAT`) from `workspace/pristine/*.bin` into `data/extracted_fields/` (gitignored) via the existing `scripts/extract_field_dat.py`.
- **Run benchmarks**: `python3 run_agent_tests.py` — feeds 3 seeded exercises (opcode byte parsing, LBA math, maplist graph logic) to `call_local_model()`. That function is a stub by default (raises `NotImplementedError`) until you wire it to a real model load — see comments in the script.
- **Verified-insight logging**: when a fix is confirmed passing on a live playtest and you say so explicitly (e.g. "it works, log it"), one JSONL row gets appended to `.workspace/verified_insights/organic_growth.jsonl` in the same `{instruction, input, output}` format as `data/ff7_re_dataset.jsonl`. This is manual/on-request only — not an automatic background process.

## Suggestions backlog

Community-prioritised encounter/engine mods: [docs/SUGGESTIONS.md](docs/SUGGESTIONS.md)
## History

Story of CSR and mods (with archived chats):
[https://individualcontributor.dev/history/](https://individualcontributor.dev/history/)
