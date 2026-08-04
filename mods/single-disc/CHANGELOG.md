# Single-disc changelog

Newest at top.

## Unreleased

- single-disc-csr-manip-movies-v0.1.0 seed: LASTFLOR, LAST4_3, LASTMAP, CANONHT2
  (id-slot overwrite on D1). inject_movies_by_disc_id.py + csr-manip-movie-seed.txt.

- CSR manip movie whitelist starter + list_d2d3_only_movies.py (inventory task)

- Renamed mod id/path from no-disc-swap to **single-disc** (builder packs,
  exclusiveGroup, docs). Same tech; player-facing name is Single-disc.

- builder: single-disc-on-csr-v0.1.1 (csr-v0.14.1) - Clean field trims + SNOVA;
  BLACKBGB Ask still CSR/Makou; FIELD.BIN left as CSR.

- Policy: single-disc not on Unmodified. Clean pack disabled.
- **Ship first:** CSR+ stacks + Highwind (core + SNOVA; no manip-movie pack).
- **Defer:** CSR base alone + required manip-movie copies (disc space).

## 0.1.1

- More FIELD Set next movie + Play movie trims from playtest (D2/D3-range sites,
  fr_e #347 after Diamond Weapon, blin70_4 #269 GameMoment>=1572, descent/lake, etc.)
- Rebuild Clean D1 builder layer from combined work bin
- Prior: Ask-for-disc removal, SNOVA + BATTLE.X LBA v3

## 0.1.0-dev

- FIELD movie trims: remove Set next movie + Play movie on crawl / missing-FMV sites
  (Tier 1 inventory + operator playtest on DuckStation)
- Keep Ask-for-disc Makou removal + SNOVA/BATTLE.X LBA v3
- Rebuild Clean D1 builder layer from combined work bin before burn

## Unreleased (0.0.0-dev)

- Clean D1 recipe: Makou Ask removal + SNOVA/BATTLE.X inject v3
- DuckStation: Ask PASS, Supernova PASS, combined PASS
- Builder: layer build script scaffold; pack not public-enabled
- Document FMV wait vs stream length (manip timing note)
