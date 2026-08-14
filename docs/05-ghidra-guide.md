# Ghidra Guide — FIELD.BIN

Start here after [03-environment-setup.md](03-environment-setup.md) phase 1 checklist.

## Create project

1. Ghidra → New Project → Non-Shared
2. Location: `~/Final-Fantasy-7-Modding/workspace/ghidra/`
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
- [x] `increment_formation` — @ `0x800ABA34`; uses `DAT_80071c20` + `g_field_rng_table`
- [x] `encounter_check` — **`0x800ABA70`** (Danger +=, dual RNG, formation pick)
- [x] `g_danger` — renamed via `lhu` @ `0x800ABC1C` (RAM `0x8007173C`)
- [x] `g_step_fraction` — renamed via lbu @ `0x800ABAB4` (RAM `0x8009C6D8`)
- [x] `field_main_loop` — `FUN_800a16cc` @ `0x800A16CC` (post-battle Danger clear)
- [x] `field_map_init` — @ `0x800BA534`; setup block `LAB_800a1dc8` / `0x800A1DC8`

## Decompiler tips

- Encounter check will reference Danger add, encounter rate division, two RNG calls
- Field load init will set up map state; look for calls near DAT section loading
- Many addresses are absolute `0x800xxxxx` — normal for PS1 Final Fantasy VII modules

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

## Exporting Field Script Data (FIELD/*.DAT)

When patching individual field scripts (e.g., LOST2.DAT for single-disc), Ghidra exports can make finding patch locations much faster than pattern-matching in Python.

### Setup for Field Script Analysis

1. **Import decompressed DAT file:**
   - Extract: `python scripts/extract_field_dat.py FIELD/LOST2.DAT workspace/tmp/LOST2.dec`
   - Ghidra → Import `workspace/tmp/LOST2.dec`
   - Format: Raw Binary
   - Language: **Data:LE:8:default** (not MIPS — field scripts are bytecode, not MIPS code)
   - Base address: `0x00000000` (relative to file start)

2. **Enable PSX plugin** (if available):
   - File → Install Extensions → PSXExecutableLoader
   - May help with FF7 opcode recognition if plugin supports field script format

### Useful Exports for Script Patching

| Export Type | How to Generate | When to Use |
|-------------|-----------------|-------------|
| **Hex Dump with ASCII** | Select region → Copy Special → Byte String | Quick pattern verification |
| **Memory Listing** | File → Export Program → ASCII | Full disassembly with addresses |
| **Annotated Hex** | Selection → Export → Intel Hex | Sharing specific script sections |
| **Raw Bytes** | Selection → Copy Special → Python Byte String | Direct paste into Python patch scripts |

### Example Workflow: Exporting LOST2 init/0 Script

**Goal:** Get annotated hex dump of the init entity's script section for patching.

1. **Find script offset** (from `field_dat.py` or prior analysis):
   ```python
   # Run once to find offset:
   python scripts/compare_field_dat.py FIELD/LOST2.DAT
   # Output shows init/0 at offset 0x434 (example)
   ```

2. **In Ghidra:**
   - Navigation → Go To → `0x434`
   - Select range (e.g., `0x434` to `0x4F0` for ~190 bytes)
   - Right-click → Copy Special → Byte String

3. **Export for sharing:**
   - File → Export Program → ASCII
   - Output file: `workspace/ghidra/LOST2-init-script.txt`
   - Include: Selected range only
   - Format: Listing with addresses and bytes

4. **Share the export:**
   - Save to `workspace/ghidra/` or `docs/ghidra-pastes/`
   - Include in documentation or chat for Agent analysis
   - Annotate key offsets (MUSIC opcodes, RET, jump targets)

### What to Include in Exports

For script patching (like v0.1.36 LOST2), most useful info:

- **Byte offsets** (relative to script start or file start)
- **Opcode values** (e.g., `0x20 = MUSIC`, `0x00 = RET`, `0x10 = JMPF`)
- **Control flow** (branches, jumps, returns)
- **Target addresses** for jumps (where JMPF/GOTO point)

### Example Export Format

```
Offset   Bytes                           Notes
------   -----                           -----
0x434    43 00 14 30 84 04 09 05        MPNAM + IFUB pattern
0x43A    20 01 00                       MUSIC id=1
0x43C    00                             RET ← patch this to JMPF
0x43D    18 ...                         IFUW (unreachable after RET)
0x463    30 xx xx ...                   AKAO ambient sounds (target)
```

### Time Savings

**Without Ghidra export:**
- Agent pattern-matches bytecode blind
- Multiple iterations to find correct offset
- Risk of patching wrong location

**With Ghidra export:**
- Agent sees exact opcode flow and addresses
- Single iteration to correct patch location
- Visual confirmation of jump targets

### Adding to Agent Workflow

When posting a script patch task to `docs/INSTRUCTIONS.md`:

1. Export the relevant script section from Ghidra (100-200 bytes around patch area)
2. Save to `workspace/ghidra/FIELDNAME-ENTITY-SCRIPT.txt`
3. Mention the export in INSTRUCTIONS so Agent can reference it
4. Agent writes patch script using exact offsets from export

This workflow was added after v0.1.36 (LOST2 JMPF patch) to avoid future blind pattern-matching.

## External references

- [Field map encounter mechanics](https://ff7speedruns.com/index.php/Field_map_encounter_mechanics)
- [Field Map RNG](https://ff7speedruns.com/index.php/Field_Map_RNG)
- [Qhimm FIELD.BIN thread](https://forums.qhimm.com/index.php?topic=6496.0)
- ff7tk `IsoArchiveFF7.cpp` — how Makou updates FIELD.BIN on save
- [FF7 Field Script Opcodes Reference](https://wiki.qhimm.com/view/FF7/Field/Script/Opcodes)
