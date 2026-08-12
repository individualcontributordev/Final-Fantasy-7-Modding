# Task: Retest manip-movies audio after v0.1.3 (Hojo CANONHT2)

## Closed

- single-disc-on-csr-v0.1.20: CANON_2 Hojo field OK (no full glitch on load)
- D1 to D2 break OK on 0.1.9+

## Open (audio)

Manip-movies had real audio plus a flickering/extra sound. Shrink-inject wrote
correct CANONHT2 bytes into CAR_1209 but left MOVIE_ID engine size as ISO
byte length + old aux, while CSR D2 uses Form2 eng size (nsec*2336) and source
aux. Player could mis-length the stream (dual/flicker audio).

## Fix

single-disc-csr-manip-movies-v0.1.3 — Form2 MOVIE_ID eng size/aux from source
disc. Auto with Single-disc when CSR+ off.

## What you do

1. Hard-refresh builder
2. Base: CSR
3. Mods: Single-disc only (CSR+ off so movies auto-include)
4. APPLIED must show:
   - single-disc-on-csr-v0.1.20
   - single-disc-csr-manip-movies-v0.1.3
5. Build Disc 1
6. Quit DuckStation fully; no CE
7. Save-state a field or two before Hojo; enter CANON_2 / play Hojo FMV path
8. Listen: one clean track, no flicker/double audio

Also spot-check any other seeded FMV you notice if easy.

## Evidence (paste)

```
APPLIED single-disc id:
APPLIED movies id:
CSR+: OFF
Hojo field load: OK / GLITCH
Hojo FMV/audio: CLEAN / FLICKER+DOUBLE / OTHER
Other FMVs notes:
Load method: in-game save / save-state (field or two before)
CE: NO
notes:
```

## When done

Commit this file with evidence, push, say check.
