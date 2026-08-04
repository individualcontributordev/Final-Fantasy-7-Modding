# Finding: CSR manip FMVs on D1 — pack split vs CSR+ stacks

**Date:** 2026-08-04
**Status:** product design (builder stacking)

## Goal

Operator: manip-movie pack is **not optional on CSR base** - always ship/enable with
no-disc-swap-on-csr. Only CSR+ stacks skip the movie pack.

Operator distinction:

- **CSR base:** certain FMVs kept for manips (FD/List etc.) - need correct streams on D1-only
  when those Plays still run.
- **CSR+:** removes/skips field FMVs - no manip-movie ISO copies needed.


- CSR base + no-disc-swap: keep manip-critical FMV streams correct (copy D2/D3
  MOVIE files onto D1 + leave Play movie for those sites).
- CSR + CSR+ scene packs + no-disc-swap: do not need those copies (scenes cut);
  avoid forcing a huge movie payload when CSR+ is selected.

## Builder constraint

Layers only add/patch bytes. Stacking CSR+ scene add-ons does not remove
files that an earlier no-disc-swap layer already injected.

So one pack that always embeds manip movies will still contain those files when
CSR+ is also enabled (usually harmless if nothing plays them; wastes space).

There is no if-CSR+-then-skip-movies inside a single layer unless the builder
UI gains conditional deps (it does not today).

## Recommended handling

### Split into two add-ons

| Pack id (example) | Contents | When to enable |
|-------------------|----------|----------------|
| no-disc-swap-on-csr-vX | Ask trims, non-manip field movie Set+Play trims (crawl/unblock), SNOVA+BATTLE.X | Always with CSR no-disc-swap |
| no-disc-swap-csr-manip-movies-vX | ISO inject of whitelist D2/D3 MOVIE only; no Play deletion for those sites | **Required** with CSR base no-disc-swap; **omit** when CSR+ scene packs are used |

User stacks:

- CSR base, single disc: Base CSR + no-disc-swap-on-csr + manip-movies (**both required**)
- CSR + CSR+ scenes, single disc: Base CSR + CSR+ scene packs + no-disc-swap-on-csr (no manip-movies)

Both stacks need SNOVA (in the core no-disc-swap-on-csr pack).

### Alternative: one fat CSR pack

Merge manip movies into no-disc-swap-on-csr (still must not use that fat pack with CSR+
if avoiding movie payload - then need a thin CSR+ variant). Split remains cleaner.

### Do not

- Put manip movie copies in Clean or Highwind no-disc-swap packs
- Engine-stub MOVIE for CSR (breaks manip timing / intro)
- Assume CSR+ can strip baked-in movies from a prior layer

## Whitelist process

1. List CSR manips that play a multi-disc FMV and need correct frames/audio.
2. Map to MOVIE files on D2/D3 + field sites.
3. Inject those files onto D1; patch movie table/indices if needed (like SNOVA LBAs).
4. For those fields: keep Set+Play (do not delete ops).
5. For non-manip crawl sites: still delete Set+Play as on Clean.

## Movie inject technical note

Field PMVIE uses per-disc indices. Copying a D2 file onto D1 may require adding
under MOVIE/ and extending the D1 table, or ID remap. Verify loader before assuming
copy file alone is enough.

## Related

- 2026-08-03-noswap-full-run-scope.md
- 2026-08-03-noswap-fmv-wait-vs-stream.md
- 2026-08-04-noswap-supernova-all-bases.md
