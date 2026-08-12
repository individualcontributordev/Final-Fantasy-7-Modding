# Task: Retest ALL seeded FMV audio (Hojo + Bugen waterfall + endings)

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
