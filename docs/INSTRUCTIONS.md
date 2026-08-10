# Single-disc + CSR+ + manip-movies (reminder)

## What you should get

| Stack | Layers |
|-------|--------|
| CSR only + Single-disc | CSR + Single-disc + CSR manip movies + ending movies |
| CSR + CSR+ + Single-disc | CSR + CSR+ scene packs + Single-disc + ending movies only (no manip-movies) |

Manip-movies = speedrun/FMV streams CSR still plays on one disc (CANONON, LASTMAP, ...).
CSR+ cuts those scenes, so those ISO copies are skipped on purpose.

Ending parts always ride with Single-disc (credits), with or without CSR+.

## Manifest rule

single-disc-csr-manip-movies-v0.1.2 autoInclude:

- when single-disc-on-csr-v0.1.2 is selected
- on base csr-v0.14.1
- unless any selected id starts with csr-plus-scene- (or CSR+ master toggle is on)

## If you still see manip-movies with CSR+ on

1. Hard-refresh the builder.
2. Check APPLIED.txt / zip name - ending packs are expected; manip-movies / csr-movies are not when CSR+ is on.
3. Say check with APPLIED.txt paste if it still lists manip-movies with CSR+.

## Builder fix (site)

autoIncludeMatches also suppresses manip-movies when the CSR+ master checkbox is on,
not only when a disc-specific csr-plus-scene-* pack is in the id list.
