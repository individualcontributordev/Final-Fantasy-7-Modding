# RESOLVED (negative) — see docs/findings/2026-08-24-canonon-hardcode-scus94163-negative-result.md
#
# The SCUS_941.63 export you already produced was fully grepped: no
# CANONON string, no id-47 branch, no field-opcode dispatcher at all in
# that executable. This file's remaining steps are stale — do not run
# them again. Next investigation (not yet scoped into instructions) is
# at the field-script level (CANONON's own field, not the kernel exe).
# Nothing further needed here for now.

# Ghidra: is CANONON's hardcoded movie seek unique to id 47? (STALE, see note above)

## Why

`docs/findings/2026-08-24-canonon-hardcode-clean-room-reverification.md`
confirmed (live emulator test) that PMVIE id 47 (CANONON) ignores a patched
`MOVIE_ID.BIN` row 47 at runtime — the real cannon movie plays regardless.
Open question this task answers: **is that special-cased for id 47 only,
or does the engine do this for other movie ids too?** This matters because
`docs/reference/movie-system.md`'s 17-movie relocation to-do list currently
*assumes* every other id honors the table — unproven.

A raw byte scan of `SCUS_941.63` already ruled out LBA 250450 appearing as
a literal (32-bit LE word or BCD MSF, both byte orders — zero hits). So
either the LBA is computed at runtime, or the engine isn't hardcoding an
LBA at all but a **filename** it resolves via a CD directory search,
bypassing `MOVIE_ID.BIN` entirely. Check both, in this order.

## What to export (do this instead of manual point-and-click hunting)

Rather than testing Hypothesis A/B by hand in the GUI one string at a time,
export the **whole decompiled program** once and I'll grep it directly —
faster and won't miss anything a manual search might skip.

### 1. Import (once, if not already done this session)

Import `SCUS_941.63` following `docs/ghidra-battle-overlays.md` §7 exactly
(extract the `.body` with the `0x800` EXE header stripped, Raw Binary, MIPS
32-bit LE, image base `0x80010000`, then Auto Analyze). Use the **same
Ghidra project** as any prior FIELD.BIN/battle imports so addresses can be
cross-referenced later. Let Auto Analyze finish completely before exporting.

### 2. Export decompiled C for the whole program

**File → Export Program...** → Format: **C/C++** (this exports the
Decompiler's C output for every function Ghidra could decompile, not just
one). Save to:

```
workspace/ghidra-exports/SCUS_941.63.decompiled.c
```

(`workspace/ghidra-exports/` is gitignored — this file stays local, never
committed. Create the folder if it doesn't exist yet.)

### 3. Export the Listing (raw disassembly + defined strings/data)

**File → Export Program...** → Format: **ASCII (Listing)**. Save to:

```
workspace/ghidra-exports/SCUS_941.63.listing.txt
```

This carries the defined-string table and data labels the C export
sometimes drops or renames, useful as a cross-check.

### 4. Tell me it's done

Once both files exist under `workspace/ghidra-exports/` on this machine,
tell me — I'll grep them for `CANONON`, other movie names (from
`docs/findings/2026-08-24-csr-movie-reachability-scan.md`), `MOVIE_ID`,
and comparisons against `47`/`0x2f`, then write the finding myself.

If either export is huge (the C export especially, for a full executable,
can be tens of MB) and slow to produce, that's fine — it's a one-time
export, not something we repeat per-hypothesis.

## What the analysis will answer (for your reference — you don't need to check this yourself)

- Whether `CANONON` (or `CANONON.MOV`) appears as a literal string in the
  executable, and if so, what function(s) reference it.
- Whether other movie names from the 17-movie to-do list also appear as
  literal strings (broader pattern) or only `CANONON` does (one-off).
- Whether the function that reads `MOVIE_ID.BIN` and indexes by row
  contains a special-case branch comparing the movie id against `47`.
- Result goes into a new dated finding under `docs/findings/`, per
  `.agents/rules/capture-research-findings.mdc`.
