# Task: confirm JUNAIR battle-return freeze trigger (RAM watch), then playtest movie relocation

## Bisect result (confirmed)

The freeze reproduces identically on `bisect_core_no_relocation.bin`
(no movie-relocation patch) and `playtest_movie_relocation.bin` — it is
**pre-existing in `single-disc-on-csr` itself**, unrelated to the movie
patch. Also confirmed: the freeze does **not** occur on stock CSR Disc 2
alone at the same spot.

Root-cause research (`docs/findings/2026-08-26-junair-single-disc-battle-return-freeze.md`):

- JUNAIR's encounter table and `BATTLE/SCENE.BIN` are **byte-identical**
  between CSR D1 and D2 — ruled out.
- The **only** real script difference between D1/D2 JUNAIR.DAT is one
  slot, `air0` entity script 3: CSR D2's copy (which single-disc merges
  wholesale) adds an `IFSW`-gated block containing an `AKAO` (`0xF2`)
  instruction — a raw CD-XA command with **literal sector/size bytes
  compiled into the script**, not looked up via `MOVIE_ID.BIN` (per
  `docs/findings/2026-08-24-akao-opcode-0xf2-is-canonon-cd-call-site.md`).
  D1's copy of this same slot has no such block. This is the leading
  suspect but not yet confirmed to be what's actually executing at the
  freeze.

## 1. RAM-watch to confirm the freeze site

Open `bisect_core_no_relocation.cue` (build command in step 2 below) in
DuckStation with the debugger. Get to JUNAIR (field 384, moment 1016),
trigger a battle, let it finish, and when the freeze happens on return to
the field, check the CPU program counter / call stack in DuckStation's
debug window.

- **If PC is stuck inside the field script interpreter executing the
  `air0` entity's script 3** (look for it looping/stuck right after
  hitting bytes `f2 00 00 00 c1 78 ...` — the `AKAO` op) → confirms the
  hypothesis above. Report back "confirmed AKAO/air0" and I'll design a
  fix (likely stripping/patching that block in the single-disc JUNAIR
  merge).
- **If PC is stuck somewhere else entirely** → the `air0` script isn't
  the cause; report back exactly what DuckStation shows (PC address,
  any visible function name, call stack) so I can look elsewhere.

If you don't have the debugger set up or this is too fiddly, that's fine
— report back "skipped RAM watch" and just do the playtest checklist
below; I'll come back to this diagnostic later.

## 2. Build BOTH images and compare

The **core build** (no movie-relocation patch) is already produced by
step 1 of the build chain below, before the `apply_layer.py` step. Build
both from scratch and keep both `.bin`s:

```
python3 mods/single-disc/scripts/build_singledisc_core_bin.py
cp workspace/iso-extract/ff7_d1_singledisc_core.bin workspace/iso-extract/bisect_core_no_relocation.bin
python3 scripts/apply_layer.py workspace/iso-extract/ff7_d1_singledisc_core.bin builder/single-disc-movie-relocation-v0.1.0/layers/disc1.layer.json -o workspace/iso-extract/playtest_movie_relocation.bin
```

Generate a `.cue` for each:

```
python3 -c "
import pathlib
for stem in ['bisect_core_no_relocation', 'playtest_movie_relocation']:
    p = pathlib.Path(f'workspace/iso-extract/{stem}.bin')
    p.with_suffix('.cue').write_text(f'FILE \"{p.name}\" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
"
```

## 3. Playtest single-disc-movie-relocation-v0.1.0 (JUNAIR / TRNAD_51 / ROOTMAP)

`docs/findings/2026-08-25-movie-relocation-plan.md` fixed the last 4 real
live movie-id conflicts in the single-disc build (agent-verified via the
byte-level scanner, not yet human-playtested). Need DuckStation
confirmation that all 3 movies actually play the right footage in-game
and nothing else broke.

(Build already done in step 1 above — use the `playtest_movie_relocation.cue`
produced there.)

## 4. Playtest checklist (DuckStation)

Boot `playtest_movie_relocation.bin`. For each field below, use a save
state or field-warp cheat to jump straight there if you have one —
otherwise reach it via normal/skip-ahead play.

1. **JUNAIR** (field id 384, Junon area) — trigger whatever event plays
   the Gelnica cutscene. Confirm the movie that plays is the **Gelnica
   cargo-plane crash** cutscene, not a Gold Saucer clip.
2. **TRNAD_51** (field id 706, Northern Crater train/canyon cluster) —
   this field has 4 duplicate `tg_d` script variants (slots 4/5/6/7)
   gated on game-state; try to trigger it at a few different points in
   the story if possible. Confirm the movies that play are the intended
   end-game cutscenes (do **not** expect to see North Corel's mine-cart
   sequence or the Junon cannon-train footage — those are the *wrong*
   clips this patch replaced).
3. **ROOTMAP** (field id 143, Mako Reactor 8 area, early Midgar) —
   confirm this still plays **MAINPLR.MOV** exactly as before (this
   field's movie was intentionally left untouched by the patch — it's
   the regression check).

## 5. Report back

Report the RAM-watch result from step 1 first (confirmed AKAO/air0, stuck
elsewhere, or skipped). Then, for each of the 3 fields in step 4, say
whether the correct movie played, and paste any DuckStation error/log
output if something looks wrong (wrong footage, black screen, crash,
audio desync). No further action needed from you beyond that — I'll
investigate anything that doesn't match.

---

# (superseded) Status: AKAO operand fetch uses 16 addressing modes, not always a literal — CANON_1/CANON_2 scanned, no literal-mode match found yet

`FUN_800bf908`/`FUN_800bee10` (AKAO's operand-fetch helpers) decompile to a
**selector-nibble dispatch**: mode 0 reads a literal straight from the
script (what the prior finding assumed universally), modes 1–0xF instead
index into global/bank variable tables. See
`docs/findings/2026-08-24-canon-fields-akao-operand-addressing-modes.md`.

Using `scripts/field_dat.py` I enumerated every AKAO (`0xF2`) instruction in
`CANON_1.DAT` (2 instructions, both cmd=0x40) and `CANON_2.DAT` (24
instructions, cmd in `{0x0,0x1,0x1E,0x3F,0x40,0x78,0x7F,0xF,0xF0}`). None
match the confirmed live-trace `a1=0xC` when decoded as literal-mode, which
is expected if the real instruction uses a non-zero selector nibble (bank
lookup) instead.

**Next step (agent-doable via existing scripts, no human Ghidra session
needed):** re-scan CANON_1/CANON_2 AKAO instructions decoding the selector
nibble properly for every instruction (not assuming mode 0), to find which
one resolves to `cmd=0xC` — either directly (mode 0) or by identifying which
bank/global variable a non-literal-mode instruction reads and what earlier
script bytecode sets that variable to `0xC`. No pending human task right
now.

---

# (superseded) Status: 0x800C47CC is a generic CD-command helper (FUN_800c46d0) — need callers of FUN_800c46d0 + FUN_800bf908 body

## Task: trace who calls FUN_800c46d0, and what FUN_800bf908 reads

`0x800C47CC` sits inside `UndefinedFunction_800c46d0`, which just builds a
5-word CD command block from `FUN_800bf908(n, offset)` lookups and then
calls the generic dispatcher — this function fires for **every** disc
read, not just movies. To find the CANONON-specific logic we need to go
one level up and one level down:

1. In Ghidra, rename `UndefinedFunction_800c46d0` to `issue_cd_command`
   (optional, just for clarity) then **right-click it → Show References
   To** (References to the function itself, not to `FUN_800c46a4`).
   Paste the full list of callers (addresses).
2. **Navigation → Go To → `FUN_800bf908`**. Open its Decompile panel.
   Paste the full decompiled body — this function takes `(n, offset)` and
   is almost certainly indexing into a per-command/per-movie parameter
   table; we need to see the table address and how `n`/`offset` map to it.
3. Same for **`FUN_800bee10`** (used for the first word, `_DAT_8009a004`)
   — paste its decompiled body too.
4. If time allows, also check **`FUN_800c46a4`** (called first, before
   the command-block build) — paste its decompiled body.

## What happens next

`FUN_800bf908`'s table is likely where the movie id (or a LBA/sector
count derived from it) enters this call chain. Once we see that table
and its indexing, we should be able to answer why CANONON's own
`MOVIE_ID.BIN` row isn't being honored.

---

# (superseded) Status: caller found (FIELD.BIN, ra=0x800C47CC) — need Ghidra to identify the function

## Task: import FIELD.BIN into Ghidra and inspect 0x800C47CC

The dynamic trace worked: at the CD dispatcher breakpoint during CANONON,
`ra=0x800C47CC` — inside FIELD.BIN's address range (base `0x800A0000`).
See `docs/findings/2026-08-24-canonon-ra-inside-field-bin.md`. This
supersedes the earlier "third module" theory below — no more DuckStation
tracing needed for now, this is a Ghidra static-analysis task.

1. Extract + decompress disc 2's `FIELD.BIN` (this is disc 2 — CANONON's
   movie id/field script live there):
   ```
   python scripts/extract_from_iso.py workspace/pristine/FINALFANTASY7_D2.bin FIELD/FIELD.BIN workspace/tmp/FIELD.BIN
   python scripts/decompress_gzipps.py workspace/tmp/FIELD.BIN workspace/tmp/FIELD.BIN.dec
   ```
2. Ghidra → new project → Import `workspace/tmp/FIELD.BIN.dec`:
   - Format: **Raw Binary**
   - Language: **MIPS: R3000 32bit little endian**
   - Base address: **`0x800A0000`**
3. **Analysis → Auto Analyze** → accept defaults → wait until the
   background task list is fully idle (check it twice a few seconds
   apart to confirm nothing new queues up).
4. **Navigation → Go To** → `0x800C47CC`.
5. Note the name/start address of the **containing function** (Ghidra
   should show it in the Function/Decompile panel).
6. Scroll up from `0x800C47CC` to see the few instructions/lines just
   before the call — specifically how `a0` (should end up as `0x7FE`),
   `a1` (`0xC`), `a2` (`0x2`), `a3` (`0x0`) are set: literal constants,
   loaded from a table, or computed from other values.
7. Use **Function → Show References To** (or right-click → References)
   on that containing function to see what calls *it* — that should
   trace back toward the actual PMVIE/MOVIE opcode handler.
8. Paste back: the function name/address at `0x800C47CC`, the
   instructions setting up `a0`-`a3`, and the list of callers from step 7.

## What happens next

Once you paste that, this should identify either the exact
movie-id → CD-command translation, or the next function up the call
chain to inspect — either way it's the concrete lead the dynamic trace
was for.

---

# (superseded) Status: static tracing exhausted — need a DuckStation dynamic trace of the CANONON movie call

## Why (skip if you already know)

Two full static-tracing passes are done and both dead-ended:
- `FIELD.BIN` (disc 2): PMVIE/MOVIE/MVIEF opcode handlers found and fully
  read, plus every function reachable from the per-frame field-object
  update loop. They only stage state in a shared struct
  (`DAT_8009c6e0`) — no CD/disc-read call anywhere.
  (`docs/findings/2026-08-24-field-bin-pmvie-movie-mvief-handlers-located.md`)
- Kernel EXE, **all three discs** (`SCUS_941.63/64/65`): CD dispatcher is
  byte-identical across discs, no literal movie-id-47 constant, and the
  movie-streaming primitive (`FUN_80033e74`, CD mode `0xb`) has **zero
  in-file callers** anywhere.
  (`docs/findings/2026-08-24-kernel-exe-all-discs-no-movie-hardcode.md`)

More grepping won't help — the call is either in a third
not-yet-found module, or it's issued through a function-pointer indirect
call the decompiler couldn't resolve to a name (so text search misses it
either way). The only way to get real evidence now is watching it happen
live in a debugger-capable emulator.

## Task: capture the call stack at the CANONON movie seek in DuckStation

**Correction (learned from first attempt):** `0x8002da7c` is the
*generic* CD-command dispatcher — it fires on **every** disc read (field
loads, textures, sound, everything), not just movies. A plain breakpoint
there is useless, it'll hit constantly. Use a **conditional
breakpoint/watchpoint on the command code value**, not just the address,
so it only stops for the movie-streaming command specifically.

You need DuckStation with the debugger enabled, and the CANONON trigger
in FF7 disc 2 (Junon cannon sequence — trigger the cutscene where the
cannon fires at Sister Ray/Weapon).

1. Open DuckStation → **Settings → Advanced → enable "Show Debug Menu"**
   (or launch a debug build) so the CPU debugger window is available.
2. Boot disc 2, load/advance a save to just before the CANONON cutscene
   triggers (Junon, after firing the cannon).
3. Open **Debug → CPU Debugger**.
4. Instead of breaking on the dispatcher address unconditionally, set a
   **memory watchpoint (write breakpoint) on `0x8009a000`**, the global
   CD-command-code variable (`DAT_8009a000` from the kernel exe — same
   address on all 3 discs). If DuckStation supports conditional
   watchpoints, set the condition to break only when the written value
   is `0xb` (the movie-streaming mode, per the finding doc). If it
   doesn't support a value condition, set an unconditional write
   watchpoint on that address — it'll be far less noisy than breaking on
   the dispatcher function itself, since most reads/writes to disc are
   quick file opens rather than command-code writes.
5. Resume emulation, let the CANONON cutscene trigger.
6. Each time the watchpoint hits, check the value just written to
   `0x8009a000` (or `$a0`/return value if DuckStation shows it inline).
   Skip any hit where the value isn't `0xb`. When you find the `0xb`
   hit, **before resuming**, capture:
   - The **call stack** (Debug → CPU Debugger's "Call Stack" panel, or
     equivalent).
   - The **return address** / the address of the instruction that wrote
     `0xb` to `0x8009a000` (tells you which function issued the movie
     seek).
   - Register values at that point, especially `$a0`-`$a3`.
7. If no hit ever shows value `0xb`, that itself is useful evidence
   (means the movie doesn't go through `DAT_8009a000` at all, or the
   command code constant isn't actually `0xb` for movies) — report that
   back instead of guessing further.
8. Paste everything you captured (call stack, return address, register
   dump, or the "no 0xb hit" result) back here — don't summarize/trim
   it, paste raw.

## What happens next

Once you paste the capture, the return address tells us which module
issued the call (its address range identifies FIELD.BIN vs kernel vs an
unknown third module) — that's the concrete lead needed to know what to
extract and decompile next. No further action needed from you until
then.

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
