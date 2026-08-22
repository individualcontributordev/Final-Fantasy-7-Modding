# Task: Test build WITHOUT the LOST2 IFUW gate fix (diagnostic, not a release)

## Why

Diagnostic question: what happens at the D1->D2 transition if we skip the
LOST2 break-scene IFUW gate fix (the single-byte patch that forces
`Var[13][0]==0xa455` open) but keep every other v0.2.3 fix (rework/safe
field merges, BLACKBGB/E/3 DSKCG fix, FIELD.BIN/WORLD.BIN table fix)?

This is **not** a new pack version — nothing was bumped in `pack.json`/
`builder/manifest.json`, and no `.layer.json` was regenerated. It's a
one-off local bin for comparison only.

## What you do

1. `git pull --ff-only`.
2. Build it:

   ```bash
   python3 -c "
   import sys
   sys.path.insert(0,'scripts')
   sys.path.insert(0,'mods/single-disc/scripts')
   from disc_sources import load_csr_image
   from build_work_bin import apply_rework_merge, apply_safe_field_merge, apply_dskcg_removal, inject_snova
   from fix_field_bin_table import fix_field_and_world_bins
   from pathlib import Path

   c1 = bytes(load_csr_image(1))
   c2 = bytes(load_csr_image(2))
   img = bytearray(c1)
   apply_rework_merge(img, c1, c2)
   apply_safe_field_merge(img)
   apply_dskcg_removal(img)
   # SKIP apply_lost2_break_fix (this is the diagnostic)
   fix_field_and_world_bins(img)
   out = Path('workspace/iso-extract/single-disc-v023-noifuw.bin')
   out.parent.mkdir(parents=True, exist_ok=True)
   out.write_bytes(img)
   inject_snova(out)
   print('done', out)
   "
   printf 'FILE "single-disc-v023-noifuw.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > workspace/iso-extract/single-disc-v023-noifuw.cue
   ```

3. Open `workspace/iso-extract/single-disc-v023-noifuw.cue` in DuckStation
   fresh. Play to the Disc 1->2 transition point (BLACKBGB field #103 ->
   LOST2). Report exactly what happens:
   - Does the break scene / MAPJUMP to COS_BTM2 fire at all?
   - If not, what does the game do instead (stuck in LOST2, dialogue
     loop, something else)?

## Evidence (paste)

```
Without IFUW fix, at LOST2: <describe exactly what happens>
```

## When done

Paste evidence, say check. (No commit needed for this diagnostic bin;
the build script one-liner above is documented here, not committed as
a new file.)

---

# Task: Playtest single-disc-on-csr v0.2.3 (fixes v0.2.2 LOST2 background corruption)

## Why

v0.2.2 fixed the D1→D2 black screen and the Makou save error, but the
forest field **LOST2 (#634)** rendered with a garbled/static background
right after the break scene (movement/audio were fine — only the
background graphics were corrupted).

Root cause: `force_lost2_break_ifuw.py` clears a single else-jump byte
in LOST2's script to open the break-scene gate, but it did this by
**decompressing the whole 32KB field, then recompressing it from
scratch** with this repo's own from-scratch LZS encoder
(`compress_all_with_header`). That encoder round-trips correctly
through this repo's own decompressor, but it can choose different
match/literal splits than the original CSR encoder for unrelated
bytes — including the 13KB background section — producing a bitstream
that decoded with visible corruption on real hardware/DuckStation even
though our own Python decoder read it back fine.

Fixed: the else-byte is now patched **directly inside the still-compressed
LZS body**, in place, without ever re-encoding the rest of the file.
Verified offline: the rebuilt `FIELD/LOST2.DAT` differs from pristine
CSR Disc 2's `LOST2.DAT` by **exactly one byte** (the intended else-jump
byte), everything else — including the entire background section byte
range — is untouched/identical to CSR D2.

Bumped to **v0.2.3**. This is a fresh playtest — confirm the D1→D2
transition/music/Makou-save fixes from v0.2.2 still hold, and that
LOST2's background now renders correctly.

The build isn't committed (`.bin`/`.cue` gitignored) — rebuilt locally
below.

## Prerequisites

- `workspace/pristine/FINALFANTASY7_D1.bin`, `_D2.bin`, `_D3.bin` present.
- `Final-Fantasy-7-CSR` repo checked out as a sibling of this repo.
- Python 3 on PATH; run all commands from this repo's root.

## What you do

1. `git pull --ff-only`.
2. Rebuild the work bin and a matching `.cue`:

   ```bash
   python3 mods/single-disc/scripts/build_work_bin.py -o workspace/iso-extract/single-disc-v023-repro.bin
   printf 'FILE "single-disc-v023-repro.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > workspace/iso-extract/single-disc-v023-repro.cue
   ```

   Expect a line `force IFUW else-byte @...: 0xb -> 0x0` and `patched in
   place: 17090 -> 17090 bytes (no recompress)` during the "Forcing
   LOST2 D1->D2 break-scene IFUW gate open..." step. No `WARNING:` or
   uncaught errors.

3. Open `workspace/iso-extract/single-disc-v023-repro.cue` in
   DuckStation fresh (no save states, no cheats).
4. New game, play through Midgar to confirm baseline sanity (no hangs).
5. Progress to the Disc 1→2 transition (BLACKBGB field #103 → LOST2 →
   break scene → COS_BTM2). Confirm:
   - Transition still goes straight to the break scene with music
     (should be unchanged from v0.2.2 — still fixed).
   - After the break scene, on LOST2 (forest): is the **background**
     rendered correctly (fixed) or garbled/static/glitched (bug still
     present)? Character models and movement were already fine before.
6. Open this bin in Makou Reactor, make a trivial edit, Save. Confirm
   it still succeeds (should be unchanged from v0.2.2).

## Evidence (paste)

```
Disc 1->2 transition: straight to break scene with music (expected)
LOST2 background: renders correctly (fixed) / still garbled (bug)
Makou save test: SUCCEEDED / FAILED (paste exact text)
notes:
```

## When done

Paste evidence above, commit this file, push, say check.
