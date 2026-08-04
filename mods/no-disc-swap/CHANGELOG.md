# No-disc-swap changelog

Newest at top.

## Unreleased

- Policy: no-disc-swap only on CSR, CSR+ stacks, and Highwind - not Unmodified/clean
  (keep Unmodified free of field/FMV changes). Clean builder pack disabled.
- CSR base: manip-movie pack is **required** (not optional); omit only with CSR+

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
