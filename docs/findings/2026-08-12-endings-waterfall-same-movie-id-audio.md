# Finding: Endings + Bugen waterfall flicker — same MOVIE audio class

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
