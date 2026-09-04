# Archive

Scripts and docs this repo used to carry. Nothing here is maintained; the links
go to the commit that removed each set, which is where the last working copy
lives. `git show <sha>^:<path>` prints a file as it was.

## Docs

| Removed | Was | Commit |
|---|---|---|
| `docs/00-goals.md` … `docs/10-patch-workflow-cheatsheet.md` | Numbered RE curriculum: encounter system, disc format, Ghidra guide and automation, burn and workstation runbooks | [`7922c1d`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/7922c1d) |
| `docs/findings/`, `docs/logs/`, pastes | Dated research notes | moved to `Final-Fantasy-7-RE-Archive` in [`97f1e9d`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/97f1e9d) |
| `articles/` | Draft write-ups on publishing PSX mods and remaking field encounters | [`1e43095`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/1e43095) |
| `CHANGELOGS.md`, `ARCHIVED.md`, `AGENTS.md` | Per-mod changelog index and agent instructions | [`7922c1d`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/7922c1d), [`3de479b`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/3de479b) |
| Nested `README.md` files under `builder/`, `workspace/` | Per-directory instructions, including Windows handoff | [`86caa2f`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/86caa2f) |
| `.cursor/skills/`, `.agent/skills/` | Ship-mod and RE-process agent skills | [`64217b8`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/64217b8) |

## Scripts

| Removed | Was | Commit |
|---|---|---|
| `mods/single-disc/scripts/*` (~25 files) | Staged CSR+ and Highwind disc-collapse pipeline: field merges, movie injection, LBA aliasing, release artifacts | [`3de479b`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/3de479b), [`ae367df`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/ae367df) — bases now live in the CSR repo |
| `scripts/field_dat.py`, `field_dat_write.py`, `ff7_opcodes.py`, `lzs.py`, `disc_sources.py` | Field script parsing, opcode tables, LZS codec | [`3de479b`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/3de479b) |
| `scripts/apply_ppf.py`, `make_ppf.py`, `build_site_docs.py` | PPF-era patch tooling, before `ic-layer-v1` | [`1e43095`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/1e43095) |
| `scripts/bin_diff_to_layer.py` | Standalone BIN differ, folded into `build_base_layer.py` | [`6bbebbd`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/6bbebbd) |
| `scripts/bootstrap_venv.py`, `libs/manifest_lock.py`, `requirements*.txt` | Venv bootstrap and manifest locking; zopfli is now the only dependency | [`565142d`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/565142d), [`3de479b`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/3de479b) |
| `scripts/edc_ecc.py` | Unused EDC/ECC helper; `repair_mode2_edc.py` owns footers | [`a7bf18b`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/a7bf18b) |
| `mods/*/scripts/build_all_rates.py` | Per-mod rate loops, replaced by `rebuild_on_base.py` | [`3de479b`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/3de479b) |
| `mods/fanfare-skip/scripts/build_battle_x.py` | Earlier BATRES.X patcher, superseded by the playtested build | [`da4e40e`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/da4e40e) |

## Mod data

| Removed | Was | Commit |
|---|---|---|
| `stub-bb7c-rate25.hex`, `-rate75.hex`, `stub-bb7c.hex`, `stub-7db4-rate25.hex`, `-rate75.hex` | Light (25%) and Dense (75%) encounter stubs, retired when the set became No Encs / Half / Double | [`f6f0c3d`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/f6f0c3d) |
| `builder/*-25/`, `builder/*-75/` packs | Published layers for those rates | [`f6f0c3d`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/f6f0c3d) |
| Retired `single-disc` builder layers | Versioned packs kept per release before unversioned ids | [`e0e81a0`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/e0e81a0), [`c9f272e`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/c9f272e) |
| Tracked `workspace/iso-extract/` binaries | Extracted game data committed by mistake; `.gitignore` covers it now | [`a7bf18b`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/a7bf18b), [`407c040`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/407c040) |
