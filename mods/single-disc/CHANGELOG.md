# Single-disc changelog

- manual edits on top of csr base + single-disc mod

## Unreleased

- LASTMAP (#768): ship Clean single-disc Set+Play removal onto CSR pack (wrong FMV on D1 after D3 merge).
- LAS4_2 (#765): ship Clean single-disc Set+Play removal onto CSR pack (Makou hits invalid archive on grown SNOVA bins).
- Operator publishes Makou-fixed work bin via docs/INSTRUCTIONS.md (bin_diff vs CSR base -> single-disc-on-csr-v0.1.1 layer).
- blackbgb (#103): remove bad JMPF+0 (forward 1 byte) Ask stand-ins; **delete** the four Ask-for-disc ops instead (fixes post-Hojo las0_1 load).

Newest at top.

## Unreleased

- Builder: single-disc movies pack uiHidden; auto-applied with CSR single-disc when no CSR+ scenes


- single-disc-on-csr: merge all CSR D2+D3 changed FIELD maps onto D1 (keep CSR D1 FIELD.BIN)
- blackbgb Ask nop + LOST2 D2 break retained; movie seed rebuilt


- single-disc-on-csr: blackbgb Ask no-op (keep Play music); LOST2 from CSR D2 (break scene)
- movie seed pack rebuilt on that core


- Operator: blackbgb Ask removed on CSR core (rebuild pack next).

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
