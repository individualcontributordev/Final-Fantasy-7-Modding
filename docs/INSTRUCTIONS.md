# Task: Build Single-disc v0.2.0 work bin with LOST2 break-scene IFUW fix

## Why

All prior BLACKBGB/DSKCG isolation builds still failed the Disc 1→2
transition. Digging into the old (retired) builder-site apply order and
git history turned up the real root cause: it was fixed once before, in
v0.1.37/v0.1.39 (`ship_v037.py`), but that fix was never ported into the
current from-scratch `build_work_bin.py` pipeline.

The actual gate isn't in BLACKBGB at all — it's in **LOST2** (the field
CSR merges D1→D2 through). LOST2's init script ends with:

```
IFUW Var[13][0] == 0xa455, else +0x0b
MAPJUMP field 526 (COS_BTM2 — the break scene)
```

On real multi-disc CSR, the disc-swap hardware event sets that GM flag,
so the IFUW falls through and MAPJUMPs into the break scene. On a
single-disc build nothing ever sets it, so the IFUW always takes the
"else" branch and skips the MAPJUMP — LOST2's init just returns and the
save prompt / break scene never fires, regardless of what's done to
BLACKBGB's DSKCG.

`build_work_bin.py` now has a new step, `apply_lost2_break_fix`, using
`mods/single-disc/scripts/force_lost2_break_ifuw.py`, which clears that
else-jump (0x0b → 0x00) after the rework merge puts CSR D2's LOST2 in
place. This build reverts to the full (non-isolated) `build_work_bin.py`
defaults — CSR D1+D2+D3 safe-field merge, DSKCG stripped from all three
disc-hub fields, SNOVA inject — plus this one new fix.

## Prerequisites

- `workspace/pristine/FINALFANTASY7_D1.bin`, `_D2.bin`, `_D3.bin` present.
- `Final-Fantasy-7-CSR` repo checked out as a sibling of this repo (i.e.
  `../Final-Fantasy-7-CSR` relative to this repo root), on its normal
  branch (CSR v0.14.1 layers under `builder/csr-v0.14.1/layers/`).
- Python 3 on PATH, run all commands from this repo's root
  (`Final-Fantasy-7-Modding/`).

## What you do

1. `git pull --ff-only` in this repo (and in the CSR repo if you keep it
   up to date separately).
2. Build the work bin with the LOST2 break-scene fix included:

   ```bash
   python3 mods/single-disc/scripts/build_work_bin.py -o workspace/iso-extract/single-disc-v0.2.0-lost2fix.bin
   ```

   Watch for this in the output near the end (before the SNOVA inject
   section):

   ```
   Forcing LOST2 D1->D2 break-scene IFUW gate open...
     force IFUW else-byte @0x4d4: 0xb -> 0x00
   ```

   If instead it prints "no gate cleared (already open, or pattern not
   found)", paste the full output — that means CSR's LOST2 changed shape
   and the fix needs re-verifying against the new bytes.
3. Generate a matching `.cue`:

   ```bash
   python3 -c "
from pathlib import Path
b = Path('workspace/iso-extract/single-disc-v0.2.0-lost2fix.bin')
c = b.with_suffix('.cue')
c.write_text('FILE \"%s\" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' % b.name, encoding='utf-8')
print('WROTE', c, c.read_text())
"
   ```
4. Open `workspace/iso-extract/single-disc-v0.2.0-lost2fix.cue` in
   DuckStation fresh (no cheats/speedhack, no save state from an older
   build).
5. Play a normal early-game sequence to confirm baseline sanity:
   - New game intro through Midgar reactor 1 bombing mission loads fine.
   - Enter/exit a few field screens without hangs or corrupted graphics.
6. Progress to the end of Disc 1 and reach **field #103 (BLACKBGB)** —
   the old "Ask for disc 2" hub. Confirm:
   - No disc-swap prompt appears (DSKCG removal still working).
   - It **does** jump into the CSR break/transition scene (save prompt
     and/or the Disc-2-opening cutscene), matching multi-disc CSR
     behavior at this point. This is the regression we're checking —
     note exactly what happens if it's still wrong.
7. If you reach a scene that would normally load an overworld save point
   (SNOVA), confirm it renders correctly.
8. Note anything unexpected: freezes, black screens, wrong field data.
   Movies aren't merged in this build, so vanilla-disc1 movie behavior
   is expected/OK for this pass.

## Evidence (paste)

```
Build script output line for LOST2 fix (paste it):
Intro -> reactor 1 bombing mission: OK / FROZE / OTHER
Field navigation (few screens): OK / GLITCHED / OTHER
BLACKBGB (#103) disc-swap prompt: ABSENT (good) / STILL APPEARS
BLACKBGB (#103) break/transition scene: FIRED CORRECTLY / BLACK SCREEN / WRONG MUSIC ONLY / STRAIGHT TO DISC2 NO BREAK / OTHER (describe)
SNOVA save point (if reached): OK / BROKEN / N/A
Load method:
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.
