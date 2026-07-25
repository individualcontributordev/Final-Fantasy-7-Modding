# Ghidra Guide — FIELD.BIN

Start here after [03-environment-setup.md](03-environment-setup.md) phase 1 checklist.

## Create project

1. Ghidra → New Project → Non-Shared
2. Location: `~/ff7-modding/workspace/ghidra/`
3. Import `workspace/iso-extract/FIELD.BIN.dec`

### Import settings

| Setting | Value |
|---------|-------|
| Format | Raw Binary |
| Language | MIPS: R3000 32bit little endian |
| Base address | **`0x800A0000`** (US FIELD.BIN module; was wrongly documented as `0x80000000`) |

If an existing project used `0x80000000`, real code/data VAs are **Ghidra_VA + `0xA0000`**. Table file `0x40638` → real **`0x800E0638`**. Prefer a fresh import at `0x800A0000` before matching DuckStation PCs.

Click Analyze → yes to defaults (MIPS analysis).

## First win: find the RNG table

1. **Search → Memory** → search all
2. Hex string: `B1 CA EE 6C 5A 71 2E 55`
3. Should be exactly one hit (256-byte table follows)
4. Label it: `g_field_rng_table`

If not found:

- Wrong binary (not decompressed FIELD.BIN?)
- Wrong region rip (table should be identical across US/EU/JP)

## Second win: find code that uses the table

**Do not rely on xrefs to the table** — often **0** after default analysis (MIPS `lui`/`addiu`).

Instead: **Search → For Scalars** (see below) for StepID / Offset / Danger, then read those functions for table loads.

If xrefs *do* appear: open them and look for StepID++ / Offset+=13 / `table[stepid] - offset`.

Label the StepID RNG helper `increment_step_id`.

## Third win: find RAM address references

**US FIELD.BIN note:** StepID is **not** encoded as `lui 0x8009` + `0xc540`. Use:

`lui …, 0x800a` then offset **`-0x3ac0`** → `0x8009C540`.

Confirmed site: ~`0x8000B9C8` (`increment_step_id`). See `01-encounter-system.md`.

**Search → For Scalars** (still useful for other vars):

| Value to search | Finds |
|-----------------|-------|
| `0x800a` | many; filter near StepID code |
| `0x9ad2c` / Offset via `-0x52d4` with `0x800a` | Offset access |
| `0x7173c` | Danger access |
| `0x71c20` | Formation access |
## Fourth win: emulator correlation

1. DuckStation → load test ISO
2. Debug → break or memory watch at `0x8009C540`
3. Walk on grass field until StepID changes
4. Note PC (program counter) when StepID updates
5. In Ghidra: **Navigation → Go To** that address
6. Should land inside or near encounter check code

If PC doesn't match Ghidra address: adjust import base address and re-analyze.

## Functions to identify (checklist)

- [x] `g_field_rng_table` — data, 256 bytes @ `0x800E0638`
- [x] `increment_step_id` — returns table[stepid] - offset @ `0x800AB9C8`
- [ ] `increment_formation` — similar, uses formation counter (`FUN_800aba34`?)
- [~] `encounter_check` — body found (dual jal + Danger); **fix function start**
- [ ] `g_danger` — rename `DAT_8007173c`
- [ ] `field_map_init` — runs on map load (hook target for reseed patch)

## Decompiler tips

- Encounter check will reference Danger add, encounter rate division, two RNG calls
- Field load init will set up map state; look for calls near DAT section loading
- Many addresses are absolute `0x800xxxxx` — normal for PS1 FF7 modules

## When ready to patch (later)

1. Find code cave (run of `00` bytes, ≥ 64 bytes free)
2. Write reseed stub at cave
3. Hook `field_map_init` entry: `jal reseed_stub`
4. Export patched bytes or note file offset for hex edit
5. Follow [04-workflow.md](04-workflow.md)

Do **not** patch until all four "win" steps above are done.

## Useful Ghidra shortcuts

| Action | Key (default) |
|--------|---------------|
| Go to address | G |
| Rename symbol | L |
| Show xrefs | Ctrl+Shift+F |
| Decompile | Ctrl+E (in listing) |
| Patch instruction | Ctrl+Shift+G |

## External references

- [Field map encounter mechanics](https://ff7speedruns.com/index.php/Field_map_encounter_mechanics)
- [Field Map RNG](https://ff7speedruns.com/index.php/Field_Map_RNG)
- [Qhimm FIELD.BIN thread](https://forums.qhimm.com/index.php?topic=6496.0)
- ff7tk `IsoArchiveFF7.cpp` — how Makou updates FIELD.BIN on save
