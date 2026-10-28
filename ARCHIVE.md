# Archive

Scripts and docs this repo used to carry. Nothing here is maintained; the links
go to the commit that removed each set, which is where the last working copy
lives. `git show <sha>^:<path>` prints a file as it was.

History was rewritten on 2026-10-28 to drop about 4.7 GB of generated layer JSON
(every `layer.json` over 1 MB, 109 distinct blobs). Those files are now a small
`stripped-by-history-rewrite` placeholder holding the original blob id and size, in
every commit that had them; all other files, commits and messages are unchanged.
Commit ids before the first stripped blob are unchanged; 847 later ones are not.
`ARCHIVE-commit-map.txt` maps each old id to its new one (`old new`, one per line).
The links below are already remapped. The full pre-rewrite history, with the real
layer JSON, is not on GitHub; rebuild the layers from the scripts and `pristine/`.

## Docs

| Removed | Was | Commit |
|---|---|---|
| `docs/00-goals.md` … `docs/10-patch-workflow-cheatsheet.md` | Numbered RE curriculum: encounter system, disc format, Ghidra guide and automation, burn and workstation runbooks | [`790991d`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/790991d) |
| `docs/findings/`, `docs/logs/`, pastes | Dated research notes | moved to `Final-Fantasy-7-RE-Archive` in [`3213793`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/3213793) |
| `articles/` | Draft write-ups on publishing PSX mods and remaking field encounters | [`1e43095`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/1e43095) |
| `CHANGELOGS.md`, `ARCHIVED.md`, `AGENTS.md` | Per-mod changelog index and agent instructions | [`790991d`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/790991d), [`dee2ee5`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/dee2ee5) |
| Nested `README.md` files under `builder/`, `workspace/` | Per-directory instructions, including Windows handoff | [`86caa2f`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/86caa2f) |
| `.cursor/skills/`, `.agent/skills/` | Ship-mod and RE-process agent skills | [`64217b8`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/64217b8) |

## Scripts

| Removed | Was | Commit |
|---|---|---|
| `mods/single-disc/scripts/*` (~25 files) | Staged CSR+ and Highwind disc-collapse pipeline: field merges, movie injection, LBA aliasing, release artifacts | [`dee2ee5`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/dee2ee5), [`98b51a1`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/98b51a1) — bases now live in the CSR repo |
| `scripts/field_dat.py`, `field_dat_write.py`, `ff7_opcodes.py`, `lzs.py`, `disc_sources.py` | Field script parsing, opcode tables, LZS codec | [`dee2ee5`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/dee2ee5) |
| `scripts/apply_ppf.py`, `make_ppf.py`, `build_site_docs.py` | PPF-era patch tooling, before `ic-layer-v1` | [`1e43095`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/1e43095) |
| `scripts/bin_diff_to_layer.py` | Standalone BIN differ, folded into `build_base_layer.py` | [`131eafb`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/131eafb) |
| `scripts/bootstrap_venv.py`, `libs/manifest_lock.py`, `requirements*.txt` | Venv bootstrap and manifest locking; zopfli is now the only dependency | [`1507db5`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/1507db5), [`dee2ee5`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/dee2ee5) |
| `scripts/edc_ecc.py` | Unused EDC/ECC helper; `repair_mode2_edc.py` owns footers | [`eb9fcfc`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/eb9fcfc) |
| `mods/*/scripts/build_all_rates.py` | Per-mod rate loops, replaced by `rebuild_on_base.py` | [`dee2ee5`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/dee2ee5) |
| `mods/fanfare-skip/scripts/build_battle_x.py` | Earlier BATRES.X patcher, superseded by the playtested build | [`0156046`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/0156046) |

## Mod data

| Removed | Was | Commit |
|---|---|---|
| `stub-bb7c-rate25.hex`, `-rate75.hex`, `stub-bb7c.hex`, `stub-7db4-rate25.hex`, `-rate75.hex` | Light (25%) and Dense (75%) encounter stubs, retired when the set became No Encs / Half / Double | [`9a4ce09`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/9a4ce09) |
| `builder/*-25/`, `builder/*-75/` packs | Published layers for those rates | [`9a4ce09`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/9a4ce09) |
| Retired `single-disc` builder layers | Versioned packs kept per release before unversioned ids | [`5682ba3`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/5682ba3), [`6190fe1`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/6190fe1) |
| Tracked `workspace/iso-extract/` binaries | Extracted game data committed by mistake; `.gitignore` covers it now | [`eb9fcfc`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/eb9fcfc), [`9cb2f29`](https://github.com/individualcontributordev/Final-Fantasy-7-Modding/commit/9cb2f29) |
