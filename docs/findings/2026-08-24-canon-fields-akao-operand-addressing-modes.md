# CANON_1/CANON_2 AKAO instructions enumerated; operand fetch uses a 16-mode addressing scheme, not raw literals

## Context

Follow-up to `2026-08-24-akao-opcode-0xf2-is-canonon-cd-call-site.md`, which
identified `FUN_800c46d0` (the `ra=0x800C47CC` call site) as opcode `0xF2`
AKAO and assumed its operand words are literal bytes from the script. That
assumption needed checking against the actual decompiled bodies of the two
helper functions AKAO calls to fetch its operands.

## Correction: `FUN_800bf908`/`FUN_800bee10` are not literal reads

Decompiling both functions (`/tmp/ghidra_out.txt`, same Ghidra headless
pipeline) shows they take `(param_1, param_2)` = (nibble selector, script
byte offset) and do:

1. Read a byte from the script at `param_2`.
2. Split it into a **nibble** (`param_1` selects high/low nibble of one of
   three adjacent script bytes) used as a 0–15 **addressing mode**, and the
   **other nibble/byte** as the actual index/value.
3. Dispatch on the addressing-mode nibble:
   - **mode 0**: value is a literal straight from the script (the case the
     original finding assumed applied universally).
   - **modes 1,3,5,7,0xB,0xD,0xF** (odd byte-return cases) / **2,4,6,8,0xC,
     0xE** (word cases): index into different global banks — `DAT_8009d288`
     (± `0x100`/`0x200`/`0x300`/`0x400` offset per mode) or a separate table
     at `0x80075e24` (mode 5/6) — i.e. bank/global-variable lookups, exactly
     like the addressing modes other field-script opcodes (`IFUW`, `SETWORD`,
     etc.) already use for their bank-relative operands.
   - Writes via `FUN_800beca4` happen for the non-literal modes when a debug
     flag (`DAT_8009d820 & 3`) is set — this is instrumentation/debug-mode
     bookkeeping, not relevant to the CD command values themselves.

So AKAO's CD-command operand words are **only** literal-from-script when
their selector nibble is 0; for other field files/instances they may pull
from bank variables. This must be checked per-instruction, not assumed.

## CANON_1 / CANON_2 AKAO instruction scan

Used `scripts/field_dat.py` (`load_field_dat_path`) to properly parse each
field's `scripts` section into per-entity/per-slot bytecode, then scanned
every slot for the `0xF2` opcode (fixed 14-byte length) and decoded the
`cmd` byte (offset+5) and two 16-bit words (offset+6, offset+8) as if in
literal mode:

**CANON_1.DAT** (740, exterior cannon-firing field) — only 2 AKAO
instructions, both in `box` slot 1:
```
fileoff 0x24d: f2 00 00 00 29 40 00 01 00 00 00 00 00 00   cmd=0x40 w1=0x100 w2=0x0
fileoff 0x292: f2 00 00 00 29 40 68 01 00 00 00 00 00 00   cmd=0x40 w1=0x168 w2=0x0
```

**CANON_2.DAT** (741, Hojo/indoor field) — 24 AKAO instructions across
`ELEC1`, `init`, and `hojyo` entities, with varied `cmd` bytes:
`{0x0, 0x1, 0x1E, 0x3F, 0x40, 0x78, 0x7F, 0xF, 0xF0}`.

## Not yet resolved

Neither field's literal-mode `cmd` byte matches the confirmed live-trace
register `a1=0xC` (assuming the `FUN_800c46d0` decompile's register mapping
`a1=cmd, a2=word@+6, a3=word@+8` holds — this mapping itself is inferred
from calling convention, not directly observed in the trace). Given the
addressing-mode finding above, this is expected if the real instruction
uses a non-zero selector nibble (bank lookup) rather than a literal — in
that case the actual sector/size value only exists at runtime in the global
bank, not as a static byte in the `.DAT`, and cannot be found by a pure
literal byte-scan of the script.

## Next steps

1. Re-scan CANON_1/CANON_2 AKAO instructions decoding the **selector
   nibble** properly (not assuming mode 0) to see if any resolve to mode 0
   with `cmd=0xC`, or identify which bank slot a non-literal-mode
   instruction would read from — then find what field-script bytecode
   elsewhere in the field sets that bank/global variable to `0xC`.
2. Alternatively, resume the DuckStation dynamic trace but this time note
   the **actual PC of the failing AKAO instruction** (via
   `DAT_800722c4`, the field-script program counter) at the moment of the
   `0x800C47CC` call, so the exact byte offset within whichever field's
   script is running is known directly instead of inferred from a literal
   pattern match.
