# CORRECTION (see bottom): opcode 0xF2 is AKAO, not PMVIE — kept for the table-location method, do not trust the PMVIE identification below

# [SUPERSEDED] field-script opcode 0xF2 handler located; operand is a literal in the field's own script, not looked up from a shared table

## Context
Continuing the CANONON (Junon Cannon, movie id 47) trace. Previously confirmed
`ra=0x800C47CC` (inside FIELD.BIN) calls a generic CD-command builder
`FUN_800c46d0`, which itself calls the CD dispatcher directly
(`func_0x8002da7c`) — see
`docs/findings/2026-08-24-canonon-caller-is-generic-cd-command-helper.md`.

## Method
Ghidra headless (`analyzeHeadless` + custom `DecompileTargets.java`
post-script) against `workspace/ghidra/FIELD.BIN.dec.bin`, loaded as raw
binary at base `0x800a0000`, MIPS:LE:32:default. Decompiled
`FUN_800c46d0`, then located its entry point's *data* references (not just
call xrefs — it had zero, since it's invoked indirectly) with a byte scan
for the little-endian pointer `0x800c46d0` in the module.

## Finding

`FUN_800c46d0`'s address appears exactly once in the module, as a **data
pointer** at `0x800e05f0`. Scanning backward from there, this is the middle
of a contiguous array of code pointers starting at `0x800e0228` (immediately
after an ASCII digit-string table, `"0123456789..."`, which ends at
`0x800e0227`).

- Table base: `0x800e0228`
- Index of `FUN_800c46d0`: `(0x800e05f0 - 0x800e0228) / 4 = 242 = 0xF2`

This is the **same 256-entry function-pointer opcode dispatch table**
already confirmed in
`docs/findings/2026-08-24-field-bin-pmvie-movie-mvief-handlers-located.md`
(`PTR_LAB_800e0228`; that doc verified opcodes `0xF8`/`0xF9`/`0xFA` at
`0x800e0608`/`0x800e060c`/`0x800e0610` via string xrefs — matching exactly
what this scan reads back at those addresses, cross-confirming the table).

`FUN_800c46d0` is the handler for opcode **`0xF2`**. Per the canonical FF7
field-script opcode table (Qhimm/ffrtt wiki: `...F0 MUSIC F1 SOUND F2 AKAO
F3 MUSVT ... F8 PMVIE F9 MOVIE FA MVIEF...`), **opcode `0xF2` is `AKAO`**
("Set Audio Command" — the field-script instruction that drives PSX CD-XA
audio/sound playback), **not PMVIE**. PMVIE is `0xF8`, confirmed separately
and already ruled out as containing no CD call.

### `FUN_800c46d0` decompiled (handler body)
```c
undefined4 FUN_800c46d0(void)
{
  if ((DAT_8009d820 & 3) != 0) {
    FUN_800bead4(&DAT_800a086c,3);
  }
  FUN_800c46a4();                                   // zero out CD command block 0x8009a000..0x8009a014
  _DAT_8009a000 = (ushort)*(byte*)(script_ptr + 4);  // read byte at script-PC+4 -> cmd code
  _DAT_8009a004 = FUN_800bee10(1,5) & 0xff;          // read byte at script-PC+5 (via bank/opcode-arg decoder)
  _DAT_8009a008 = (int)FUN_800bf908(2,6);            // read word at script-PC+6
  _DAT_8009a00c = (int)FUN_800bf908(3,8);            // read word at script-PC+8
  _DAT_8009a010 = (int)FUN_800bf908(4,10);           // read word at script-PC+10
  _DAT_8009a014 = (int)FUN_800bf908(6,0xc);          // read word at script-PC+12
  func_0x8002da7c();                                 // CD dispatcher — the movie/seek call
  script_pc += 0xe;                                  // advance interpreter PC past this 14-byte instruction
  return 0;
}
```

`FUN_800bee10`/`FUN_800bf908` are the general-purpose "read a script operand,
optionally resolving it through variable banks (const/global/mapvar/etc. —
selected by the high nibble of `param_1`)" helpers used by *every* opcode
handler, confirmed by their huge caller lists (100+ call sites across nearly
all `FUN_800c*`/`FUN_800d*` opcode handlers). `param_1=1..6` here all select
bank 0 (`case 0` in both switches: literal immediate straight out of the
current field's script bytecode), so **every operand PMVIE uses — including
the movie ID that becomes part of the CD command — is a literal constant
compiled into that specific field's own script data**, not indexed from any
table shared across fields.

## Implication for the original question (why is MOVIE_ID.BIN ignored for CANONON)

This settles it: `MOVIE_ID.BIN` (or whatever movie-ID remap table the
original hypothesis assumed) is **never read by this code path at all**.
The 14-byte **AKAO (`0xF2`)** instruction embedded directly in the CANNON
field file's own compiled script contains the CD command parameters (cmd
code, disc-relative sector/size fields) as **hardcoded literals**, read
straight out of that field's script bytecode by `FUN_800bee10`/
`FUN_800bf908` (bank-0/literal case) and passed unmodified into the CD
dispatcher. This directly explains the confirmed live-trace `ra=0x800C47CC`
(inside `FUN_800c46d0`, this same AKAO handler) — it is the actual call
site that triggers the CANONON disc read, not `PMVIE`/`MOVIE`/`MVIEF`
(`0xF8`/`0xF9`/`0xFA`, previously shown to only stage state in a struct
with no CD call — see
`2026-08-24-field-bin-pmvie-movie-mvief-handlers-located.md`).

**AKAO is normally a CD-XA audio-track command** (music/sound streaming),
but the PSX XA subsystem's underlying CD read command is shared between
audio and full-motion video streaming — the field script apparently issues
the CANONON movie's disc read via an `AKAO`-opcode CD command rather than
through the `PMVIE`/`MOVIE` state machine, which is why patching
`MOVIE_ID.BIN` (which only the `PMVIE`/`MOVIE` id-to-LBA lookup path would
consult) has no effect on this specific scene: the sector/size values are
**literal constants compiled into the CANNON field's own AKAO instruction**,
never touching a movie-id table at all.

## Next steps
1. Identify the CANNON field's `.DAT` filename/ID (likely `jcanon`/similar in
   the field name table) and locate its script section inside `FIELD.BIN`.
2. Find the specific `AKAO` (`0xF2`) instruction in the CANONON field script
   whose literal operand bytes (script-PC+4..+13) decode to the CD command/
   sector values matching the confirmed live-trace registers
   (`a0=0x7FE, a1=0xC, a2=0x2, a3=0x0`) to pinpoint the exact byte offset.
3. Cross-check against `FIELD.BIN`'s field/script table format
   (`docs/01-encounter-system.md` / `docs/02-disc-format.md` if it documents
   the script header) to compute the exact file offset to patch, then
   confirm patching those bytes changes/disables the CANONON movie in a
   live DuckStation test.

## Cross-reference

`2026-08-12-single-disc-canon2-akao-dskcg-strip.md` (unrelated bug, same
CANON field family) independently confirms AKAO sub-opcodes are present and
sensitive to byte-level corruption in this exact field's script data
(`0e 03` DSKCG/ASK payload pairs) — consistent with AKAO being a
distinct, carefully-encoded opcode class in these field scripts, not
evidence against the 0xF2=AKAO identification here.
