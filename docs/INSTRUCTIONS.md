# Status: PMVIE/MOVIE/MVIEF handlers found — no Ghidra action needed right now

`docs/findings/2026-08-24-field-bin-pmvie-movie-mvief-handlers-located.md`
found the real opcode dispatch table (`PTR_LAB_800e0228`) and the PMVIE
(0xF8)/MOVIE (0xF9)/MVIEF (0xFA) handler addresses in the exports already
in the repo (`workspace/ghidra/FIELD.BIN.dec_disc2.c` /
`.dec_disc2.html`). The movie id is confirmed written to struct offset
`DAT_8009c6e0+2`, but no CD-read call has been found in any handler yet —
`FUN_800c0248` (called from MVIEF) and `FUN_800bc438`/`FUN_800bc4d4`
(the per-frame update path) are both ruled out as unrelated (generic
opcode-operand decoder; UI icon overlay, respectively).

Next step is more grepping of the **existing** export (agent-only, no
Ghidra session needed): read the five still-unread sibling calls inside
the per-frame update function `FUN_800ba65c` — `FUN_800bb3a8`,
`FUN_800d7d6c`, `FUN_800d7f9c`, `FUN_800d4bfc`, `FUN_800bc338` — looking
for whichever one polls `DAT_80071c1c` or resolves the movie id at
`DAT_8009c6e0+2` to an LBA/CD call. Nothing for you to do here until that
turns up a new dead end or a concrete address worth confirming live.

---

# (superseded) Ghidra: find the PMVIE movie-id → LBA resolver inside FIELD.BIN (not the kernel exe)

## Why

`docs/findings/2026-08-24-canonon-hardcode-clean-room-reverification.md`
confirmed (live emulator test) that PMVIE id 47 (CANONON) ignores a patched
`MOVIE_ID.BIN` row 47 at runtime — the real cannon movie plays regardless.
`docs/findings/2026-08-24-canonon-hardcode-scus94163-negative-result.md`
then fully grepped the kernel executable (`SCUS_941.63`) and found **no**
`CANONON` string, no id-47 branch, and — most importantly — **no
field-script opcode dispatcher at all** (no per-opcode `case` switch that
would call PMVIE's handler). That's the real signal: the kernel exe never
runs field-script bytecode. **`FIELD.BIN` does** — per
`docs/02-disc-format.md`, `FIELD.BIN` decompresses to "field engine code +
data tables", i.e. it's a separate overlay module, not just a data
container. The PMVIE opcode handler — and whatever resolves a movie id to
an LBA or filename — has to live there.

There's already a `workspace/ghidra/FIELD.BIN.dec.c` export in the repo
history, but it was grepped and came back with zero hits for
`PMVIE`/`MOVIE`/`CdControl`/`CdRead`/`MOVIE_ID`. I don't have evidence for
*why* — I don't know if that export covers the whole binary or was scoped/
generated some other way, and I'm not asserting a cause without checking
(per `.agents/rules/verified-reference-evidence.mdc`). Before redoing any
import, answer this first — it's fast and avoids a wasted re-import if the
existing export is actually fine:

### 0. Check the existing export first

In your Ghidra project with `FIELD.BIN.dec` already imported (the one
`docs/05-ghidra-guide.md`'s checklist was built from):

1. **Window → Script Manager** or just check the **bottom-right
   background task list** — is anything still queued/running from a prior
   session? (Should be empty/idle.)
2. **Analysis → Auto Analyze** (or Ctrl+Shift+A) → **run it again** on the
   already-imported program, even if you think it's done. If it says
   "already analyzed, nothing to do" that confirms it's complete. If it
   finds and processes new areas, that confirms the earlier pass was
   partial — note which outcome you got.
3. Either way, once it reports idle/complete, redo the two exports below
   from that same project (no need to re-import).

### 1. Fresh import (only if you don't have a usable FIELD.BIN.dec project already)

1. Extract + decompress if you don't already have a current copy. `FIELD.BIN`
   is a top-level file under `FIELD/`, not a per-map `.DAT` — use
   `extract_from_iso.py` (not `extract_field_dat.py`, which always appends
   `.DAT` and will fail with "missing FIELD.BIN.DAT"), then decompress its
   GZIPPS header with `decompress_gzipps.py`:
   ```
   python scripts/extract_from_iso.py workspace/pristine/FINALFANTASY7_D2.bin FIELD/FIELD.BIN workspace/tmp/FIELD.BIN
   python scripts/decompress_gzipps.py workspace/tmp/FIELD.BIN workspace/tmp/FIELD.BIN.dec
   ```
   (Use disc 2 — that's the disc CANONON's `MOVIE_ID.BIN` row and field
   script live on.)
2. Ghidra → **new** project → Import `FIELD.BIN.dec`:
   - Format: **Raw Binary**
   - Language: **MIPS: R3000 32bit little endian**
   - Base address: **`0x800A0000`** (per `docs/05-ghidra-guide.md`)
3. **Analysis → Auto Analyze** → accept defaults → wait for the
   background task list to go idle.

### 2. Export decompiled C for the whole program

**File → Export Program...** → Format: **C/C++** → save to:

```
workspace/ghidra-exports/FIELD.BIN.decompiled.c
```

### 3. Export the Listing

**File → Export Program...** → Format: **ASCII (Listing)** → save to:

```
workspace/ghidra-exports/FIELD.BIN.listing.txt
```

### 4. Tell me it's done

Once both files exist under `workspace/ghidra-exports/`, tell me — I'll
grep for the field-opcode dispatch switch (look for a `case` on the PMVIE
opcode value), any `CdControl`/`CdRead`-style calls, `MOVIE_ID`, and
comparisons against `47`/`0x2f`, then write the finding.

## What the analysis will answer (for your reference — you don't need to check this yourself)

- Whether `FIELD.BIN` contains the field-script opcode dispatcher at all
  (it must, somewhere — this confirms Ghidra resolved it this time).
- Whether that dispatcher's PMVIE case reads `MOVIE_ID.BIN` normally, or
  branches specially for id 47.
- Whether `CANONON`/`CANONON.MOV` appears as a literal string, and what
  references it.
- Result goes into a new dated finding under `docs/findings/`, per
  `.agents/rules/capture-research-findings.mdc` — including, if the
  original `FIELD.BIN.dec.c` zero-hit result turns out to have been from
  an incomplete analysis pass, a **false-lead note** explaining that so
  future sessions don't trust a partial export as if it were exhaustive.
