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
| Base address | `0x80000000` |

Click Analyze → yes to defaults (MIPS analysis).

## First win: find the RNG table

1. **Search → Memory** → search all
2. Hex string: `B1 CA EE 6C 5A 71 2E 55`
3. Should be exactly one hit (256-byte table follows)
4. Label it: `g_field_rng_table`

If not found:

- Wrong binary (not decompressed FIELD.BIN?)
- Wrong region rip (table should be identical across US/EU/JP)

## Second win: find code that reads the table

1. Click `g_field_rng_table`
2. **References → Show References to Address**
3. Open each xref → you want a function that:
   - Increments a byte (StepID)
   - Compares/wraps and adds `0x0D` (13) to another byte (Offset)
   - Loads from table indexed by StepID
   - Subtracts Offset

Label that function `increment_step_id`.

## Third win: find RAM address references

**Search → For Scalars** (one at a time):

| Value to search | Finds |
|-----------------|-------|
| `0x9c540` | StepID access |
| `0x9ad2c` | Offset access |
| `0x7173c` | Danger access |
| `0x71c20` | Formation access |

MIPS pattern for `0x8009C540`:

```mips
lui   $reg, 0x8009
lbu   $reg, 0xc540($reg)    ; load StepID
```

## Fourth win: emulator correlation

1. DuckStation → load test ISO
2. Debug → break or memory watch at `0x8009C540`
3. Walk on grass field until StepID changes
4. Note PC (program counter) when StepID updates
5. In Ghidra: **Navigation → Go To** that address
6. Should land inside or near encounter check code

If PC doesn't match Ghidra address: adjust import base address and re-analyze.

## Functions to identify (checklist)

- [ ] `g_field_rng_table` — data, 256 bytes
- [ ] `increment_step_id` — returns table[stepid] - offset
- [ ] `increment_formation` — similar, uses formation counter
- [ ] `encounter_check` — calls increment_step_id twice, compares Danger
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
