# Single-disc changelog

Newest at top.

## 0.1.2

- **DEL1 (#441):** main pack keeps CSR Disc 1 file (removes jump to DEL2 #442). Confirmed vs CSR Disc 1.
- **BLACKBGB (#103):** keeps single-disc Ask removal (zero DSKCG); not raw CSR.
- **LOST2 (#634):** main pack matches CSR Disc 2 break scene (already on pack).
- **Movies policy:** latest pack is cumulative. `single-disc-csr-manip-movies-v0.1.2` =
  previous seed (v0.1.0) + LBA 250450 alias (v0.1.1) in **one** layer. Only 0.1.2 is
  enabled/auto-included. Older 0.1.0 and 0.1.1 stay in the repo/manifest but
  disabled (same exclusive group; do not stack two movie packs).
- Field tools: compare_field_dat / extract_field_dat / put_field_dat for multi-disc map checks.
- Prefer list: mods/single-disc/patches/csr-field-disc-prefer.txt (seven maps still review for later).
- Builder id: single-disc-on-csr-v0.1.2 (v0.1.1 main pack disabled).

## 0.1.1

- Restore CSR DEL1 on main pack (no jump to DEL2); prior merge had regressed.
- BLACKBGB: delete four Ask-for-disc ops (not JMPF+0 stand-ins).
- LOST2 from CSR Disc 2 break scene retained.
- manip-movies v0.1.0 seed (CANONON to JAIROFAL, CANONHT2, LAST4_3, LASTMAP) + MOVIE_ID patches.
- manip-movies v0.1.1: raw Form2 CANONON at ISO LBA 250450 (LOSLAKE1 D2-style seek).
- Field Set+Play movie trims (fr_e, blin70_4, WHITE2, LASTMAP, LAS4_2, etc.).
- SNOVA + BATTLE.X LBA inject; Ask-for-disc Makou removal.
- Movies pack uiHidden; auto-applied with Single-disc on CSR when no CSR+ scenes.
- Policy: single-disc for CSR/Highwind, not Unmodified (clean pack retired).

## 0.1.0-dev

- FIELD movie trims on crawl / missing-FMV sites.
- Ask-for-disc removal + SNOVA/BATTLE.X LBA v3.
- Clean D1 builder layer scaffold.

## 0.0.0-dev

- Clean D1 recipe scaffold; DuckStation Ask/SNOVA/combined PASS notes.
