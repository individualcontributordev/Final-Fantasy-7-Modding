# Task: Build Single-disc v0.2.0 work bin directly (bypass builder site)

## Why

v0.2.0 (built via the builder site) failed at the Disc 1→2 transition:
field #103 (BLACKBGB) does not prompt to save or jump into the CSR
Disc-2 break scene. We're isolating whether that's a builder-layer/apply
bug or a genuine bug in the merge scripts by building the raw work bin
straight from the Python pipeline (no builder site, no layer diff/apply
round-trip) and testing that directly in DuckStation.

This produces the **same** fields+DSKCG+SNOVA pipeline as v0.2.0
(`mods/single-disc/scripts/build_work_bin.py`), just built and boot-tested
locally instead of through https://individualcontributor.dev/builder/.

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
2. Build the work bin:

   ```bash
   python3 mods/single-disc/scripts/build_work_bin.py -o workspace/iso-extract/single-disc-v0.2.0-direct.bin
   ```

   This applies the 9-field rework merge, the 66-field safe merge, DSKCG
   removal (expect "Total DSKCG removed: 19"), and the SNOVA D3→D1 inject
   in one pass. Watch for any `WARNING` lines in the output and paste them
   into evidence below if present.
3. Write a matching `.cue` next to it so DuckStation can load it:

   ```bash
   python3 -c "
from pathlib import Path
b = Path('workspace/iso-extract/single-disc-v0.2.0-direct.bin')
c = b.with_suffix('.cue')
c.write_text('FILE \"%s\" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' % b.name, encoding='utf-8')
print('WROTE', c, c.read_text())
"
   ```
4. Open `workspace/iso-extract/single-disc-v0.2.0-direct.bin`'s `.cue` in
   DuckStation fresh (no cheats/speedhack, no save state from an older
   build).
5. Play a normal early-game sequence to confirm baseline sanity:
   - New game intro through Midgar reactor 1 bombing mission loads fine.
   - Enter/exit a few field screens without hangs or corrupted graphics.
6. Head to a location or two known to hit **merged-in D2/D3 fields**
   (e.g. Junon area, Cosmo Canyon, or wherever LOST2/COS_BTM/COS_BTM2/
   DEL1/JUNAIR2/BUGIN1A/NIVGATE/RCKTIN2 fields are reachable) — confirm no
   crashes, no missing/garbled field geometry or scripts.
7. Progress to the end of Disc 1 and reach **field #103 (BLACKBGB)** —
   the old "Ask for disc 2" hub. Confirm:
   - No disc-swap prompt appears (DSKCG removal working).
   - It **does** jump into the CSR break/transition scene (save prompt
     and/or the Disc-2-opening cutscene), matching multi-disc CSR
     behavior at this point. This is the specific regression we're
     checking — note exactly what happens if it's still wrong (black
     screen? wrong music? straight to Disc-2 field with no break at
     all?).
8. If you reach a scene that would normally load an overworld save point
   (SNOVA), confirm it renders correctly.
9. Note anything unexpected: freezes, black screens, wrong field data.
   Movies aren't merged yet in this build, so vanilla-disc1 movie
   behavior is expected/OK for this pass.

## Evidence (paste)

```
Build script output (paste any WARNING lines, or "no warnings"):
Intro -> reactor 1 bombing mission: OK / FROZE / OTHER
Field navigation (few screens): OK / GLITCHED / OTHER
D2/D3 merged field(s) visited (name which): OK / BROKEN / OTHER
BLACKBGB (#103) disc-swap prompt: ABSENT (good) / STILL APPEARS
BLACKBGB (#103) break/transition scene: FIRED CORRECTLY / BLACK SCREEN / WRONG MUSIC ONLY / STRAIGHT TO DISC2 NO BREAK / OTHER (describe)
SNOVA save point (if reached): OK / BROKEN / N/A
Load method:
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.
