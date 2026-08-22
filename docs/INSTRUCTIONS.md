# Task: Isolate why v0.2.1 is worse than v0.2.0 (black screen + still broken save)

## Why

v0.2.1 playtest came back **worse** than expected: no transition at all
(black screen, no audio) and Makou save still fails "Invalid archive".
Since v0.2.1 only added the `fix_field_bin_table.py` table-fix step on
top of what v0.2.0 already had, and the LOST2 IFUW patch logic was
verified byte-identical in old vs new pipeline (same 3 occurrences,
same offsets, same else-bytes 0x12/0x12/0xb — the patch is correctly
targeting the pre-MAPJUMP gate), the table-fix step is the prime
suspect for the new black-screen regression.

This step builds a diagnostic bin with the **same field merges +
LOST2 fix but WITHOUT the table-fix and WITHOUT SNOVA inject**, to see
if removing the table-fix alone restores at least the old (v0.2.0)
black-screen-but-editable-and-saveable behavior.

The build isn't committed — rebuilt locally below. Produces
`workspace/iso-extract/notablefix-test.bin` (747,435,024 bytes).

## Prerequisites

- `workspace/pristine/FINALFANTASY7_D1.bin`, `_D2.bin`, `_D3.bin` present.
- `Final-Fantasy-7-CSR` repo checked out as a sibling of this repo.
- Python 3 on PATH; run all commands from this repo's root.

## What you do

1. `git pull --ff-only`.
2. Rebuild the diagnostic bin and cue:

   ```bash
   python3 - <<'PYEOF'
import sys
sys.path.insert(0, 'scripts')
sys.path.insert(0, 'mods/single-disc/scripts')
from disc_sources import load_csr_image
from psx_mode2_iso import extract_file, replace_file_within_sectors
from merge_rework_fields import SLOT_SPLICE_FIELDS, WHOLE_FILE_FIELDS, merge_slots
from merge_safe_fields import find_safe_whole_file_merges
from remove_dskcg import remove_dskcg_from_field
from force_lost2_break_ifuw import force_lost2_ifuw
from lzs import compress_all_with_header, decompress_all_with_header

c1 = bytes(load_csr_image(1))
c2 = bytes(load_csr_image(2))
img = bytearray(c1)

for field, disc in WHOLE_FILE_FIELDS.items():
    src = c1 if disc == 1 else c2
    path = f'FIELD/{field}.DAT'
    data = extract_file(src, path)
    replace_file_within_sectors(img, path, data)
for field, slot_discs in SLOT_SPLICE_FIELDS.items():
    merge_slots(img, field, slot_discs, c1, c2)

merges = find_safe_whole_file_merges()
src_imgs = {2: bytes(load_csr_image(2)), 3: bytes(load_csr_image(3))}
for field, disc in sorted(merges.items()):
    path = f'FIELD/{field}.DAT'
    data = extract_file(src_imgs[disc], path)
    current = extract_file(bytes(img), path)
    if data != current:
        replace_file_within_sectors(img, path, data)

for field in ['BLACKBGB','BLACKBGE','BLACKBG3']:
    path = f'FIELD/{field}.DAT'
    raw = extract_file(bytes(img), path)
    new_raw, removed = remove_dskcg_from_field(raw, field)
    if removed:
        replace_file_within_sectors(img, path, new_raw)

path = 'FIELD/LOST2.DAT'
raw = extract_file(bytes(img), path)
dec = bytearray(decompress_all_with_header(raw))
forced = force_lost2_ifuw(dec)
print('forced', forced)
new_raw = compress_all_with_header(bytes(dec))
replace_file_within_sectors(img, path, new_raw)

out = 'workspace/iso-extract/notablefix-test.bin'
open(out, 'wb').write(img)
print('wrote', out, len(img))
PYEOF
   printf 'FILE "notablefix-test.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > workspace/iso-extract/notablefix-test.cue
   ```

   Expect `forced [(1236, 11)]` and `wrote ... 747435024`.

3. Open `workspace/iso-extract/notablefix-test.cue` in DuckStation
   fresh (no save states, no cheats).
4. New game, confirm no early hangs.
5. Progress to the Disc 1→2 transition. Report exactly what happens:
   straight to break scene with music / disc-2 prompt / black screen
   with no audio (same as v0.2.1) / black screen but this time note if
   ANYTHING happens (any sound, any delay before black).
6. Open this bin in Makou Reactor, make a trivial edit, Save. Report:
   succeeds / fails with "Invalid archive" / fails with other text
   (paste exact text).

## Evidence (paste)

```
Disc 1->2 transition: <result>
Music/audio: <present/absent>
Makou save test: <result, exact error text if any>
notes:
```

## When done

Paste evidence above, commit this file, push, say check.
