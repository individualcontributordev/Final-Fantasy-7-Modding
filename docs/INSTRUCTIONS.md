# Task: No-disc-swap — ioslake3 missing FMV (not freeze)

## Report

Map **ioslake3** S0 Main: Bugenhagen idle/animated, FMV should play and does not.
Not a freeze hardlock (per operator).

Script not yet on this clone — push dump when ready.

## Decision for Clean no-disc-swap

Default product policy: **leave Play movie** (wrong/missing FMV OK if story continues).

Trim in Makou **only if**:
- the map never advances after the movie wait, or
- you want polish (skip empty stare) and will rebuild the pack layer

If trimming: delete Play movie (+ optional Set next movie); **keep Jump** and bits.

## Please confirm

    ioslake3 eventually continues after wait: yes / no / unknown
    Want pack trim for polish: yes / no
    Script dump pushed: path or pending

Say check.

## Out of scope

- Global MOVIE opcode stub
- Full D2/D3 movie import for Clean (unless a specific file is tiny and required)
