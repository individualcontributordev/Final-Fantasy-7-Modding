# Patch Workflow Cheatsheet: Confirm Before You Patch

Command sequences that use `scripts/field_pattern_finder.py` and
`scripts/duckstation_addr_advisor.py` to confirm an address/opcode offset
*before* writing bytes, instead of trial-and-error patching. Both tools tag
every result `[CONFIRMED]` or `[UNCONFIRMED: <reason>]` — see
`scripts/README.md` "Verification contract" for what those mean.

Prerequisite reading: `docs/05-ghidra-guide.md` (RAM address ground truth),
`docs/04-workflow.md` (general patch/playtest loop).

## Scenario 1: "I need to patch a field script opcode (e.g. change a MUSIC id, fix a JMPF)"

1. Find every occurrence of the opcode in the target field:
   ```bash
   python3 scripts/field_pattern_finder.py pristine:1 --field LOST2 --opcode MUSIC
   ```
2. Every hit is `[CONFIRMED]` (structural parse via `field_dat.py`) — pick
   the `entity`/`slot`/`section0_off` you want.
3. If you only have a raw byte guess (e.g. from a hex-editor eyeball), check
   whether it's really an opcode start, not mid-operand garbage:
   ```bash
   python3 scripts/field_pattern_finder.py pristine:1 --field LOST2 --hex f052
   ```
   `[UNCONFIRMED: not opcode-boundary aligned]` means don't patch there —
   it's inside another opcode's operand bytes.
4. Extract, edit, re-inject:
   ```bash
   python3 scripts/extract_field_dat.py --from pristine:1 --field LOST2 -o /tmp/LOST2.DAT
   # ... hex edit at the CONFIRMED offset ...
   python3 scripts/put_field_dat.py --bin workspace/iso-extract/work.bin \
     --field LOST2 --dat /tmp/LOST2.DAT
   ```

## Scenario 2: "I have a candidate RAM address/function from an old note or Ghidra auto-analysis — is it trustworthy?"

```bash
python3 scripts/duckstation_addr_advisor.py 0x800AB9C8
python3 scripts/duckstation_addr_advisor.py increment_step_id
```

- `[CONFIRMED]` → matched `docs/05-ghidra-guide.md`'s checklist, meaning a
  human already did the DuckStation PC-correlation step. Safe to build a
  hook/stub against it.
- `[UNCONFIRMED: auto-analysis only, no emulator correlation]` → only
  Ghidra's automatic analysis found it (`scripts/ghidra/*.json`). Do the
  "Fourth win: emulator correlation" steps in `docs/05-ghidra-guide.md`
  before trusting it for a patch.
- No matches at all → search `scripts/ghidra/field-functions.json` by
  address range manually, or re-run Ghidra analysis
  (`scripts/ghidra/analyze_field_bin.py`).

## Scenario 3: "I'm looking at a non-FIELD.BIN binary (battle overlay, world, main exe)"

```bash
python3 scripts/duckstation_addr_advisor.py 0x800a2314 --binary battle
```

These binaries have no `docs/05-ghidra-guide.md`-style checklist yet, so
every hit is `[UNCONFIRMED: no checklist doc for this binary]` even if it's
in the JSON. Treat as a starting point for manual Ghidra + DuckStation
correlation (see `docs/ghidra-battle-overlays.md` for battle overlays), not
a patch-ready address.

## Scenario 4: "Nothing found by either tool"

- `field_pattern_finder.py`: confirm the field name is correct
  (`python3 scripts/query_ff7_ids.py field <name>`) and that the opcode
  mnemonic matches `scripts/ff7_opcodes.py`'s `OPCODE_NAMES` exactly.
- `duckstation_addr_advisor.py`: confirm `--binary` matches which `.BIN`
  you're actually looking at; re-run
  `scripts/ghidra/analyze_field_bin.py`-style extraction if the JSON is
  stale or empty (e.g. `field-symbols.json` is currently empty — only
  `field-functions.json` has auto-analysis data).
- Either way: state "not found by tooling" plainly rather than guessing an
  address — that's the failure mode this cheatsheet exists to prevent.
