# FF7 PSX add-on layers

Stackable `ic-layer-v1` disc patches (MIPS stubs + data bytes) for NTSC-U FF7. `README.md` is the full workflow; this is the map.

## Rules
- `python`, not `python3` (Windows Store shim). `pip install zopfli` is required. Run from repo root.
- Never edit `workspace/pristine/`. Never commit `.bin`/`.cue`/game data. `builder/*.json` stays LF.
- Layers are pinned to a base build: bump a base → recut every mod on it (`scripts/ff7mod.py rebuild all`).
- Chain publish steps with `|| break`, else a stale layer verifies `PASS`.
- Commit as `individualcontributordev <contributorindividual@gmail.com>`.

## New mod, fastest path
1. Copy the closest `mods/*/scripts/` as the template: `fanfare-skip` (MIPS stub in overlay), `field-random-encounters` / `world-map-random-encounters` (parametrised stub), `new-game-plus` (site list: path/offset/expected/replacement, guarded writes), `party-recolor` (TIM/palettes), `masamune` (mesh + field script diff), `diamond-weapon-speed-up` (worldscript in `WM0.EV`), `frame-counter`.
2. Locate code: `python scripts/sym.py NAME` / `ADDR [-o overlay]` → decomp name + `.dec` file offset. `sym.py overlays` lists load addresses (overlays collide at `0x800A0000`, `0x801B0000`, `0x801D0000`).
3. Disassemble/decompile in Ghidra (MCP; `use_program` then `decompile_function_by_address`). Write the stub as asm (`armips:*` skills) or Ghidra-style C via `scripts/c_to_mips.py` (needs zig).
4. Overlays are GZIPPS: `decompress_gzipps.py` → patch `.dec` → `compress_gzipps.py` (must fit the ISO slot) → `psx_mode2_iso.replace_file_padded`.
5. `ff7mod.py new` → `rebuild` → `verify` → `validate_manifest.py` → push `main`.

## References (read-only; `external/` is gitignored)
- `external/ff7-decomp` — Xeeynamo decomp. Symbol maps in `config/symbols.*.us.txt`; structs/Savemap in `include/game.h`; C per overlay in `src/`. **No license: read for facts (addresses, layouts); never copy its source into this repo.** Re-clone: `git clone https://github.com/Xeeynamo/ff7-decomp external/ff7-decomp`.
- `external/makoureactor` — field script opcodes/formats. `external/ff7tk` — save/data formats. `external/FF7WorldMap` — world map.
- `ff7-route/NOTES.md` — verified RAM/encounter/field-table facts; `ff7-route/tools/` parse field/world data.
- `workspace/ghidra/` — SCUS decompile dumps (gitignored). `workspace/pristine/` — retail BINs.
- Skills: `duckstation:*` (emulator MCP), `ghidra:*`, `armips:*`, `psx-spx:*` (hardware), `romhacking:*`.
- Evaluated, not needed: `mstan/Final-Fantasy-VII` (static recompiler). Its symbol tables are imported from ff7-decomp (already here); its hooks/codegen don't apply to disc patching. Only useful fact: overlay load addresses, now in `sym.py`.

## Testing
- Boot `cache/<mod-id>/FINALFANTASY7_D<n>.bin` from **this** repo, never the CSR repo's cache. Leave the user's DuckStation (port 2345) alone; use another instance (e.g. 2400).
- DuckStation `load_state` swaps the disc to the path stored in the state. After loading, check `get_disc_info.media_path`; if wrong, `disc_control insert` the right bin and `save_state` to a fresh slot.
- Memory-card saves taken before the scripted event beat save states for script-driven changes (RAM keeps old values).
