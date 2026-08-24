# CANONON CD-dispatch call issued from inside FIELD.BIN, not the kernel

**Date:** 2026-08-24
**Confidence:** confirmed
**Status:** open
**Related:** [field-bin-pmvie-movie-mvief-handlers-located](2026-08-24-field-bin-pmvie-movie-mvief-handlers-located.md), [kernel-exe-all-discs-no-movie-hardcode](2026-08-24-kernel-exe-all-discs-no-movie-hardcode.md)

## Summary

Live DuckStation breakpoint at the CD dispatcher (`0x8002DA7C`) during the
CANONON cutscene shows the return address `ra=0x800C47CC` — an address
inside FIELD.BIN's load range (base `0x800A0000`), not the kernel EXE.
This directly contradicts the prior conclusion that FIELD.BIN's
PMVIE/MOVIE/MVIEF handlers only stage state with no CD-read call.

## Context

Two static-tracing passes (see Related) dead-ended: FIELD.BIN's opcode
handlers appeared to only write to a shared state struct, and the kernel's
CD dispatcher/movie-streaming primitive had zero in-file callers anywhere.
Conclusion at the time was the real call must be in a third,
not-yet-found module. This session ran the dynamic-trace task from
`docs/INSTRUCTIONS.md` instead of more static grepping.

## Discovery

Register dump at the breakpoint hit (hit count 30) on `FUN_8002da7c`
(`0x8002DA7C`, `addiu sp,sp,-48` — function entry), captured via
DuckStation CPU Debugger screenshots:

```
pc = 0x8002DA7C   (breakpoint address, function entry)
ra = 0x800C47CC   (return address — the caller)
sp = 0x801FFE90
a0 = 0x000007FE
a1 = 0x0000000C
a2 = 0x00000002
a3 = 0x00000000
```

`ra=0x800C47CC` minus FIELD.BIN's documented Ghidra base address
`0x800A0000` (`docs/05-ghidra-guide.md`) = offset `0x247CC` into the
decompressed FIELD.BIN module — a plausible in-range offset (the RNG
table alone lives at `0x800E0638`, i.e. offset `0x40638`, so the module
spans well past `0x247CC`).

This means: the call into the generic CD dispatcher during the CANONON
movie sequence is issued from **FIELD.BIN code**, not the kernel EXE and
not some undiscovered third module.

## How we found it

Per the DuckStation dynamic-trace task in `docs/INSTRUCTIONS.md`:
breakpoint set on `0x8002DA7C` (the CD dispatcher entry, same address on
all 3 discs per `2026-08-24-kernel-exe-all-discs-no-movie-hardcode.md`).
It fired constantly (confirmed noisy/generic, expected), but hit 30
landed during the actual CANONON cutscene. Register values were read
directly from the DuckStation Registers panel via full-resolution
screenshots (raw text was not available; screenshots at zoom-in size
were legible for register values, though not for the Stack panel/hex
memory dump in the same session).

## Why it matters

Reopens the FIELD.BIN hypothesis that the prior grep-based pass
(`2026-08-24-field-bin-pmvie-movie-mvief-handlers-located.md`) seemingly
ruled out. That pass's `FIELD.BIN.dec.c` export was later deleted from
the repo (large-file cleanup) without being re-verified as exhaustive —
this new evidence suggests either that export's Auto Analyze pass was
incomplete, or the actual caller function at `0x800C47CC` wasn't reached
by the xref/string-grep approach used (e.g. reached via an indirect
call/function pointer, or a function without a recognizable
PMVIE/MOVIE/MVIEF string nearby).

`a0=0x7FE` at dispatcher entry doesn't match the previously-hypothesized
streaming-mode constant `0xb` from `FUN_80033e74`'s calling convention —
this may be a different, movie-specific CD command path (e.g. a sector
count, file number, or LBA — not a raw command mode), meaning
`FUN_80033e74`/mode `0xb` may not even be the right primitive to look for.

## False leads hit along the way

- Assumed the kernel-only static grep (all 3 discs, byte-identical CD
  dispatcher, zero in-file callers to the streaming primitive) meant the
  caller had to be outside both FIELD.BIN and the kernel. The dynamic
  trace shows the caller **is** in FIELD.BIN's address range — the static
  pass's "no hits" result for FIELD.BIN was a false negative, not
  evidence the call lives elsewhere.

## Follow-ups

- [ ] Re-extract + decompress FIELD.BIN (disc 2) and re-import into Ghidra
      at base `0x800A0000` (existing exports were deleted from the repo
      during the large-file cleanup earlier in this session).
- [ ] Navigate to `0x800C47CC` in Ghidra, identify the containing
      function, and read backward from the call site to see how
      `a0=0x7FE`, `a1=0xC`, `a2=0x2`, `a3=0x0` are constructed (literals?
      loaded from a table indexed by movie id? computed from
      `MOVIE_ID.BIN` data?).
    - `a0=0x7FE` = 2046 decimal — check whether this is a sector count,
      a raw LBA fragment, or a file/movie index before assuming it's a
      CD command mode.
- [ ] Trace what calls the function at `0x800C47CC` — that should lead
      back to the actual PMVIE/MOVIE opcode handler and, from there, to
      wherever movie id 47 gets resolved to this specific call.
- [ ] Re-run auto-analysis fully to completion before exporting this
      time, and note explicitly whether the earlier `FIELD.BIN.dec.c`
      export was generated after a complete or partial analysis pass
      (can no longer be checked directly since the file was deleted, but
      document going forward).

## Sources

- Live DuckStation CPU Debugger screenshots, breakpoint hit #30 on
  `0x8002DA7C`, CANONON cutscene (Junon, disc 2).
- `docs/05-ghidra-guide.md` — FIELD.BIN base address `0x800A0000`.
