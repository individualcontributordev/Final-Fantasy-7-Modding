# 0x800C47CC is inside a generic CD-command helper, not movie-specific code

**Date:** 2026-08-24
**Confidence:** confirmed
**Status:** open
**Related:** [canonon-ra-inside-field-bin](2026-08-24-canonon-ra-inside-field-bin.md)

## Summary

Ghidra decompile of the function containing `0x800C47CC` shows it's a
generic CD-command-issuing helper (`UndefinedFunction_800c46d0`) that
builds a 5-word command block via table lookups and calls the CD
dispatcher — it fires for every disc read, not just movies. The
movie/CANONON-specific logic must be one or more levels up (whoever calls
this helper) or inside the lookup function `FUN_800bf908`.

## Discovery

FIELD.BIN.dec (disc 2), function at `0x800C46D0` (return address
`0x800C47CC` lands right after its call to the dispatcher):

```c
undefined4 UndefinedFunction_800c46d0(void) {
  short sVar1;
  short *psVar2;

  if ((DAT_8009d820 & 3) != 0) {
    FUN_800bead4(&DAT_800a086c,3);
  }
  FUN_800c46a4();
  _DAT_8009c400 = (ushort)(byte)(_DAT_8009c6dc + (uint)(ushort)(...));
  _DAT_8009a004 = FUN_800bee10(1,5);
  _DAT_8009a004 = _DAT_8009a004 & 0xff;
  sVar1 = FUN_800bf908(2,6);
  _DAT_8009a008 = (int)sVar1;
  sVar1 = FUN_800bf908(3,8);
  _DAT_8009a00c = (int)sVar1;
  sVar1 = FUN_800bf908(4,10);
  _DAT_8009a010 = (int)sVar1;
  sVar1 = FUN_800bf908(6,0xc);
  _DAT_8009a014 = (int)sVar1;
  func_0x0002da7c();                 // <-- ra=0x800C47CC is right after this
  psVar2 = (short *)((uint)DAT_800722c4 * 2 + -0x7ff7ce04);
  *psVar2 = *psVar2 + 0xe;
  return 0;
}
```

`FUN_800bf908(n, offset)` is called 4x with different `(n, offset)`
pairs — looks like indexing a parameter table by command/word slot. This
is very likely a generic "populate CD command struct" routine reused by
every disc I/O path (reads, movies, batle/tutor async ops — consistent
with the shared "pending async op" struct noted in
`2026-08-24-field-bin-pmvie-movie-mvief-handlers-located.md`).

Separately, `References to FUN_800c46a4` (called first inside this
function, before the command-block build) shows 9 callers:
`0x800ba62c`, `0x800c46f8`, `0x800c482c`, `0x800c4964`, `0x800c4a14`,
`0x800c4a68`, `0x800c4abc`, `0x800c4b10`, `0x800d5758`. Several of these
(`800c46f8`..`800c4b10`) are inside the same function block as
`800c46d0` itself, suggesting a jump-table / state-machine reentry
pattern rather than literal recursion.

## Why it matters

Confirms `0x800C47CC` is **not** the movie-specific decision point — it's
downstream, generic plumbing. The actual "which movie / which LBA" logic
must be in whatever populates the table `FUN_800bf908` reads from, or in
one of `FUN_800c46d0`'s own callers (not yet identified — only callers of
the *inner* `FUN_800c46a4` were captured this session).

## Follow-ups

- [ ] Get references TO `FUN_800c46d0` itself (not `FUN_800c46a4`).
- [ ] Decompile `FUN_800bf908` and `FUN_800bee10` — find the table they
      index into.
- [ ] Decompile `FUN_800c46a4` (called first, before the command block).

## Sources

- Ghidra CodeBrowser, `FIELD.BIN.dec_disc2` project, decompile of
  `UndefinedFunction_800c46d0` and references-to view for `FUN_800c46a4`.
