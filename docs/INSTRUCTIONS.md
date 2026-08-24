# Ghidra: is CANONON's hardcoded movie seek unique to id 47?

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

## Setup (once)

Import `SCUS_941.63` following `docs/ghidra-battle-overlays.md` §7 exactly
(extract the `.body` with the `0x800` EXE header stripped, Raw Binary, MIPS
32-bit LE, image base `0x80010000`, then Auto Analyze). Use the **same
Ghidra project** as any prior FIELD.BIN/battle imports so addresses can be
cross-referenced later.

For the generic "search a string/scalar and follow its xrefs" mechanics
used below, see `docs/05-ghidra-guide.md` → "Reusable technique: find a
hardcoded string/constant and its callers".

## Hypothesis A — hardcoded filename string (check first, cheaper)

1. String-search for `CANONON` (the on-disc name is `CANONON.MOV`, but
   search the bare stem too in case the extension isn't stored with it).
2. If found, follow xrefs to the containing function(s) and decompile.
3. Repeat the same string search for 2-3 *other* movie names from the
   17-movie to-do list — pick short, distinctive ones from
   `docs/findings/2026-08-24-csr-movie-reachability-scan.md` (e.g.
   `GELNICA`, `RCKTOFF`, `NRCRL`).
   - **Only** `CANONON` exists as a bare string, others don't exist
     anywhere in `SCUS_941.63` → supports "id 47 is a one-off," not a
     general pattern.
   - **Multiple** movie names show up hardcoded → the table-bypass is a
     broader pattern — note exactly which ids/names.

## Hypothesis B — hardcoded/computed LBA (only if A finds nothing)

1. String-search for `MOVIE_ID.BIN` (the table's on-disc filename) to find
   the function that opens/reads the table.
2. Decompile it and trace forward to where it multiplies a movie id by the
   row size (20 bytes, per `docs/reference/movie-system.md`) to index into
   the table and read the LBA field.
3. Around that indexing/read code, look for a **comparison against literal
   `47` / `0x2f`** with a branch that **skips** the table read. Scope a
   scalar search for `0x2f` to this one function to find it fast.
4. If found, decompile the branch target — literal LBA load? call to a
   different table? something else? Note the address and behavior.
5. If no such branch exists near the table-read code: the special-case (if
   any) isn't in the generic lookup function — it may be inlined
   per-caller instead. Report that as the answer rather than searching
   further ad hoc.

## What to report back

- Function address(es) + a short decompile excerpt, written into a **new
  dated finding** under `docs/findings/` (not just chat), per
  `.agents/rules/capture-research-findings.mdc`.
- Whether the special case is keyed on a literal id (`47` only) or
  something broader (field name, a set of ids, etc.).
- If neither hypothesis hits anywhere in `SCUS_941.63`, repeat the same
  string/scalar searches against the `FIELD.BIN` import instead
  (field-script-side special case rather than kernel-side).
