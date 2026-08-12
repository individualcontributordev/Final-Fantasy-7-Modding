#!/usr/bin/env python3
"""Docs: endings + waterfall flicker share MOVIE_ID / stack pad issues."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main() -> int:
    (ROOT / "docs/INSTRUCTIONS.md").write_text(
        """# Task: Retest ALL seeded FMV audio (Hojo + Bugen waterfall + endings)

## Context

Same class of bug as Hojo flicker: wrong MOVIE_ID Form2 eng size/aux and/or
image not sector-aligned after manip-movies growth (broke endings stack).

## Fixes already on CDN / main

1. single-disc-on-csr-v0.1.20 — CANON_2 AKAO OK
2. single-disc-csr-manip-movies-v0.1.3 — Form2 MOVIE_ID eng size/aux for seed
   (CANONHT2, CANONON/JAIROFAL, LAST4_3, LASTMAP)
3. apply_layer (Python) + builder layer.js — pad grown images to 2352 so
   movies then endings stack stays sector-aligned

Bugen waterfall (LOSLAKE1) uses MOVIE_ID id 47 — same row as CANONON seed into
JAIROFAL; v0.1.3 should fix that path too when movies pack is on.

Endings pack already used Form2 eng sizes; they need a sector-aligned base
from the fixed layer apply (hard-refresh builder required).

## What you do

1. Hard-refresh builder (must pick up layer.js pad fix)
2. Base: CSR
3. Mods: Single-disc only, CSR+ off (movies + endings auto)
4. APPLIED must include:
   - single-disc-on-csr-v0.1.20
   - single-disc-csr-manip-movies-v0.1.3
   - single-disc-endings-v0.1.0-part1..part7
5. Build Disc 1; quit DuckStation fully; no CE
6. Test audio (one clean track, no flicker/double):
   a. Hojo CANONHT2 path
   b. Bugen / Cosmo waterfall lake FMV (LOSLAKE1 id47 / related)
   c. Ending credits movies

Save-state a field or two before each scene.

## Evidence (paste)

```
APPLIED single-disc:
APPLIED movies:
APPLIED endings parts: YES/NO
CSR+: OFF
Hard-refresh builder: YES

Hojo FMV audio: CLEAN / FLICKER / OTHER
Bugen waterfall FMV audio: CLEAN / FLICKER / OTHER / NOT REACHED
Ending FMV audio: CLEAN / FLICKER / OTHER / NOT REACHED

Load method:
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.
"""
    )
    print("INSTRUCTIONS ok")

    (
        ROOT / "docs/findings/2026-08-12-endings-waterfall-same-movie-id-audio.md"
    ).write_text(
        """# Finding: Endings + Bugen waterfall flicker — same MOVIE audio class

**Date:** 2026-08-12
**Status:** movies v0.1.3 + apply_layer/layer.js sector pad; retest
**Report:** Ending movies and Bugen waterfall FD manip also had flicker audio

## Shared causes

1. **MOVIE_ID Form2 eng size/aux** — manip seed rows (id7 CANONHT2, id47 CANONON
   in JAIROFAL slot) must use source nsec*2336 + aux. Fixed in movies v0.1.3.
2. **Image not multiple of 2352 after movies grow** — Python apply_layer only
   padded modifiedBytes when originalBytes == post-record len (always false after
   growth). Left size 766084029 (mod 2349). Endings then applied on broken image.
   Fixed: pad using baseline_len before records + force 2352 align if grew.
   Builder layer.js same pad.

## Bugen waterfall

CSR+ COTA trims LOSLAKE1 scripts. Waterfall FMV on CSR D2 LOSLAKE1 uses
MOVIE_ID id 47 (CANONON on multi-disc). Single-disc seed puts CANONON into
JAIROFAL and patches id47 — same row the lake path uses when disc id is 1.

## Endings

single-disc-endings-v0.1.0 parts already store Form2 eng sizes for SMK/SOUTHMK/
MONITOR/MAINPLR when applied alone. Need sector-aligned image after movies.

## Retest

Full stack + hard-refresh builder. See docs/INSTRUCTIONS.md.
"""
    )

    fr = ROOT / "docs/findings/README.md"
    t = fr.read_text()
    needle = "endings-waterfall-same-movie-id"
    line = (
        "| 2026-08-12 | endings+waterfall same FMV audio class | "
        "`2026-08-12-endings-waterfall-same-movie-id-audio.md` |\n"
    )
    if needle not in t:
        lines = t.splitlines(True)
        out = []
        inserted = False
        for ln in lines:
            out.append(ln)
            if (not inserted) and ln.startswith("| 2026-"):
                out.append(line)
                inserted = True
        if not inserted:
            out.append("\n" + line)
        fr.write_text("".join(out))
        print("findings README updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
