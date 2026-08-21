# Task: Minimal isolation build (LOST2+BLACKBGB only) — verify Disc 1→2 break scene

## Why

Previous test bins changed ~65-70 fields at once (all CSR D1/D2/D3 field
merges + all 3 DSKCG removals + SNOVA), so when something's still wrong we
can't tell which change is responsible. This build strips it down to the
**minimum** needed for the Disc 1→2 break-scene transition:

- `BLACKBGB` (field #103): DSKCG ("ask for disc") ops removed — no other
  disc's fields touch this transition.
- `LOST2`: whole file replaced with CSR D2's version — this is the *only*
  field whose CSR D1 vs D2 diff matters here (it adds the version entity
  and the `IFUW Var[13][0]==0xa455 → MAPJUMP field 526 (COS_BTM2)` break
  scene jump that D1's LOST2 lacks).
- LOST2's IFUW gate forced open (0x0b → 0x00), since the `0xa455` flag is
  only ever set by real disc-swap hardware and single-disc never sets it.
- `FIELD.BIN`'s embedded (location,size) table patched for just these 2
  resized fields (2 entries, not 71) — required for Makou saves to work,
  see `fix_field_bin_table.py`.

Everything else — the other 7 "rework" fields (COS_BTM, COS_BTM2, DEL1,
JUNAIR2, BUGIN1A, NIVGATE, RCKTIN2), the ~55-field bulk "safe" D2/D3
merge, BLACKBGE/BLACKBG3 DSKCG removal, and SNOVA injection — is **not**
included in this build. Base is otherwise plain CSR D1.

If this minimal build still hangs/black-screens at the same spot, that
narrows the bug to LOST2/BLACKBGB/COS_BTM2 or the FIELD.BIN fix itself
(not to some interaction with the other 65 fields). If it works here but
the full build doesn't, that points at one of the fields intentionally
left out (COS_BTM2 taking CSR D1 instead of pristine D1 is one candidate,
since COS_BTM2 is the break scene's own destination field).

## Prerequisites

- `workspace/pristine/FINALFANTASY7_D1.bin`, `_D2.bin` present (D3 not
  needed for this build — no SNOVA).
- `Final-Fantasy-7-CSR` repo checked out as a sibling of this repo.
- Python 3 on PATH; run all commands from this repo's root.

## What you do

1. `git pull --ff-only` in this repo (and CSR repo if applicable).
2. Build the minimal bin:

   ```bash
   python3 -c "
import sys
sys.path.insert(0, 'scripts')
sys.path.insert(0, 'mods/single-disc/scripts')
from pathlib import Path
from disc_sources import load_csr_image
from psx_mode2_iso import extract_file, replace_file_within_sectors
from remove_dskcg import remove_dskcg_from_field
from force_lost2_break_ifuw import force_lost2_ifuw
from fix_field_bin_table import fix_field_and_world_bins
from lzs import compress_all_with_header, decompress_all_with_header

c1 = bytes(load_csr_image(1))
c2 = bytes(load_csr_image(2))
img = bytearray(c1)

data = extract_file(c2, 'FIELD/LOST2.DAT')
replace_file_within_sectors(img, 'FIELD/LOST2.DAT', data)

raw = extract_file(img, 'FIELD/BLACKBGB.DAT')
new_raw, removed = remove_dskcg_from_field(raw, 'BLACKBGB')
if removed:
    replace_file_within_sectors(img, 'FIELD/BLACKBGB.DAT', new_raw)
print(f'BLACKBGB DSKCG removed: {removed}')

raw = extract_file(img, 'FIELD/LOST2.DAT')
dec = bytearray(decompress_all_with_header(raw))
forced = force_lost2_ifuw(dec)
for off, old in forced:
    print(f'force IFUW else-byte @{off:#x}: {old:#x} -> 0x00')
new_raw = compress_all_with_header(bytes(dec))
replace_file_within_sectors(img, 'FIELD/LOST2.DAT', new_raw)

fixed = fix_field_and_world_bins(img)
print(f'Total table entries patched: {fixed}')

out = Path('workspace/iso-extract/single-disc-v0.2.1-minimal-lost2.bin')
out.write_bytes(img)
print(f'Wrote {out} ({len(img):,} bytes)')
"
   ```

   Expect: `BLACKBGB DSKCG removed: 4`, one IFUW force line, and
   `Total table entries patched: 2`. If any of those differ, paste full
   output before playtesting.

3. Generate a matching `.cue`:

   ```bash
   python3 -c "
from pathlib import Path
b = Path('workspace/iso-extract/single-disc-v0.2.1-minimal-lost2.bin')
c = b.with_suffix('.cue')
c.write_text('FILE \"%s\" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' % b.name, encoding='utf-8')
print('WROTE', c, c.read_text())
"
   ```

4. Open `workspace/iso-extract/single-disc-v0.2.1-minimal-lost2.cue` in
   DuckStation fresh (no cheats/speedhack, no save state from an older
   build).
5. Play a normal early-game sequence to confirm baseline sanity:
   - New game intro through Midgar reactor 1 bombing mission loads fine.
   - Enter/exit a few field screens without hangs or corrupted graphics.
6. Progress to end of Disc 1, reach field #103 (BLACKBGB). Confirm:
   - No disc-swap prompt (DSKCG removal working).
   - It **does** jump into the break/transition scene (COS_BTM2), or
     note exactly what happens if not (black screen, freeze, wrong
     field, straight to disc 2 with no break scene, etc).
7. Optional: open this bin in Makou Reactor, make a trivial edit, Save —
   confirm it succeeds (sanity-checks the FIELD.BIN table fix on this
   smaller edit set too).

## Evidence (paste)

```
Build script output (DSKCG removed / IFUW force line / table entries patched):
Intro -> reactor 1 bombing mission: OK / FROZE / OTHER
Field navigation (few screens): OK / GLITCHED / OTHER
BLACKBGB (#103) disc-swap prompt: ABSENT (good) / STILL APPEARS
BLACKBGB (#103) break/transition scene: FIRED CORRECTLY / BLACK SCREEN / OTHER (describe)
Makou save test (optional): SUCCEEDED / FAILED / SKIPPED
notes:
```

## When done

Commit this file with evidence, push, say check.
