# Task: Build v0.2.1 with FIELD.BIN/WORLD.BIN table fix; verify Makou save + Disc 1→2

## Why

Root cause found for "Makou Reactor says Invalid archive when I try to save
one of your builds" (it opens fine, edit fine, but Save always fails).

`build_work_bin.py` resizes ~70 `FIELD/*.DAT` files (CSR field merges) via
`replace_file_within_sectors`, which correctly patches the ISO9660
directory record's size — but **`FIELD/FIELD.BIN`** (and `WORLD/WORLD.BIN`)
each embed their own internal lookup table of every field's
`(sector_location, byte_size)`, used by the PS1 engine to find each field
inside the disc. Our build never updated that internal table, so it still
had the pristine/CSR pre-merge sizes.

ff7tk (the library behind Makou Reactor) runs an unconditional step on
*every* save — `IsoArchiveFF7::reorganizeModifiedFilesAfter()` — which
rewrites `FIELD.BIN`/`WORLD.BIN` by searching their internal table for each
field's *current* `(location, size)` pair. Since our sizes disagreed with
the table, that search failed ("Error not found!"), and ff7tk aborted the
whole save with "Cannot update game binaries" (`Archive::InvalidError`).
This makes every save fail, unrelated to what was actually edited.

New step `fix_field_bin_table.py` (wired into `build_work_bin.py` right
after all field-resizing steps) patches all 71 stale `FIELD.BIN` table
entries — and checks `WORLD.BIN`'s table too (0 entries needed it this
time) — then recompresses both within their original ISO slot's byte
budget. Verified locally: a built bin has zero
`(location,size)`-table mismatches after this fix (previously 71), and the
standalone fix script round-trips cleanly against the existing v0.2.0 bin.

This is a distinct, real, and previously-unaddressed structural bug —
separate from (and possibly a factor in) the still-open Disc 1→2 black
screen issue, since the PS1 engine likely also trusts `FIELD.BIN`'s
internal table to locate field data, not just the raw ISO directory
record. This build re-tests both.

## Prerequisites

- `workspace/pristine/FINALFANTASY7_D1.bin`, `_D2.bin`, `_D3.bin` present.
- `Final-Fantasy-7-CSR` repo checked out as a sibling of this repo.
- Python 3 on PATH; run all commands from this repo's root.
- Makou Reactor built/available (`~/makoureactor`), for the save test.

## What you do

1. `git pull --ff-only` in this repo (and CSR repo if applicable).
2. Build:

   ```bash
   python3 mods/single-disc/scripts/build_work_bin.py -o workspace/iso-extract/single-disc-v0.2.1-fieldbin-fix.bin
   ```

   Watch for this near the end (before "Injecting SNOVA"):

   ```
   Patching FIELD.BIN/WORLD.BIN embedded (location,size) tables...
     FIELD/FIELD.BIN table: BLACKBG3.DAT @58244 size 22203 -> 22204
     ... (71 total lines) ...
     Total table entries patched: 71
   ```

   If it prints `Total table entries patched: 0` or a different count,
   paste full output — CSR's field sizes changed and this needs re-check.

3. Generate a matching `.cue`:

   ```bash
   python3 -c "
from pathlib import Path
b = Path('workspace/iso-extract/single-disc-v0.2.1-fieldbin-fix.bin')
c = b.with_suffix('.cue')
c.write_text('FILE \"%s\" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' % b.name, encoding='utf-8')
print('WROTE', c, c.read_text())
"
   ```

4. **Makou save test** (the actual regression this fixes):
   - Open `workspace/iso-extract/single-disc-v0.2.1-fieldbin-fix.bin` in
     Makou Reactor.
   - Make any trivial change (e.g. open a field, don't even need to edit
     anything — just File → Save, or nudge one script byte).
   - Confirm Save **succeeds** with no "Invalid archive" error. This is
     the primary pass/fail check for this task.

5. **DuckStation playtest** — same steps as before, to see if this also
   moves the needle on the Disc 1→2 transition:
   - Open the `.cue` fresh (no cheats/speedhack, no save state from an
     older build).
   - New game intro through Midgar reactor 1 bombing mission loads fine.
   - Enter/exit a few field screens without hangs or corrupted graphics.
   - Progress to end of Disc 1, reach field #103 (BLACKBGB). Confirm no
     disc-swap prompt, and note exactly what happens at the break/transition
     point (still black screen? does it now proceed? different symptom?).

## Evidence (paste)

```
Build script output line "Total table entries patched: N" (paste it):
Makou Reactor Save after opening the built bin: SUCCEEDED / FAILED (error text)
Intro -> reactor 1 bombing mission: OK / FROZE / OTHER
Field navigation (few screens): OK / GLITCHED / OTHER
BLACKBGB (#103) disc-swap prompt: ABSENT (good) / STILL APPEARS
BLACKBGB (#103) break/transition scene: FIRED CORRECTLY / BLACK SCREEN / OTHER (describe)
notes:
```

## When done

Commit this file with evidence, push, say check.
