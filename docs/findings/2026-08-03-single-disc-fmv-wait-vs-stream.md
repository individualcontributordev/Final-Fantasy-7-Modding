# Finding: Wrong FMV often shorter than wait — manip timing may still hold

**Date:** 2026-08-03
**Status:** operator observation (DuckStation); policy input for CSR single-disc
**Confidence:** likely for Clean wrong-stream case; confirm per manip on CSR

## Observation

On Clean single-disc (MOVIE left vanilla), when a D2/D3 movie id resolves to the
wrong stream on D1, the video often does not play full length, but
gameplay continues as if the original beat completed.

## Interpretation

Field MOVIE wait is not necessarily "until this STR file EOF". A separate
duration / script wait / List tick path can span the authored time while
the XA/stream ends early. Wrong video is cosmetic; time advanced for manips
that key off List (or similar) during FMV windows can still match if that
wait is duration-based rather than stream-EOF-based.

## Product impact

| Stack | Implication |
|-------|-------------|
| Clean + single-disc | Wrong FMV OK; no need to import D2/D3 movies for timing alone |
| CSR base + single-disc | Prefer leave MOVIE; only copy manip-critical files if a specific manip needs the correct frames/audio, not only wall-clock. Default: try without movie copies; add whitelist only on proven FAIL |
| CSR+ / Highwind | Trims remove plays; no movie copy |

## Not proven

- Every CSR manip FMV window uses the same wait model
- Console identical to DuckStation for early stream end
- Audio-only desync vs List

## Next

If a CSR manip fails with wrong FMV, note whether List/mtimer diverged or only
visuals wrong — then decide file copy vs scene trim.
