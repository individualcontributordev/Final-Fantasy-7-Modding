# Status: import disc-2/3 kernel EXEs into Ghidra, export decompiled C

Static tracing of `FIELD.BIN` (see
`docs/findings/2026-08-24-field-bin-pmvie-movie-mvief-handlers-located.md`)
has exhausted every function reachable from the PMVIE/MOVIE/MVIEF opcode
handlers with no `CdControl`/`CdRead`-style call found. Only the **disc-1**
kernel EXE (`SCUS_941.63`) has been decompiled so far
(`workspace/ghidra/SCUS_941.63_disc1.c`) — CANONON is a **disc-2** cutscene
(LOSLAKE1), so a disc-1-only kernel export could be missing whatever
disc-2/3-specific movie-streaming logic exists.

The disc-2/3 kernel EXEs have already been extracted from the pristine
ISOs (raw `PS-X EXE`, not GZIPPS — do not run `decompress_gzipps.py` on
these) and are sitting at:

```
workspace/iso-extract/battle-dec/SCUS_941.64_D2.body   (disc 2 kernel EXE)
workspace/iso-extract/battle-dec/SCUS_941.65_D3.body   (disc 3 kernel EXE)
```

**Task for you (Ghidra, one program per file):**

For each `.body` file above:

1. **File → Import File...** → select the `.body` file
2. Format: **Raw Binary**
3. Language: **MIPS · 32-bit little-endian**
4. Open the program
5. **Window → Memory Map** → set image base to **`0x80010000`**
6. **Analysis → Auto Analyze...** → run with defaults, wait for the
   background task list to go idle
7. Sanity check: **G** (Go To) → `80014540` should land on a thin wrapper
   function that calls `80033E34` (per `docs/ghidra-battle-overlays.md`
   §7.2 — same recipe used for the existing disc-1 `SCUS_941.63` project).
   If it lands on garbage/no function, the image base or file offset is
   wrong — re-check step 5.
8. **File → Export Program...** → Format: **C/C++** → save to:
   - `workspace/ghidra/SCUS_941.64_disc2.c` (for the D2 file)
   - `workspace/ghidra/SCUS_941.65_disc3.c` (for the D3 file)

Once both exports exist under `workspace/ghidra/`, tell me — I'll grep
both for the CD-command dispatcher (`FUN_8002da7c`-equivalent /
`DAT_8009a000` writers) and cross-reference the `FUN_80033e74`/
`FUN_80033cb8(0xb, ...)` streaming-mode call sites already found in the
disc-1 export, looking for any disc-2/3-specific movie path that isn't
present on disc 1.

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
