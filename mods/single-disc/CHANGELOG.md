# Single-disc changelog

Newest at top.

## 0.1.8 (undo LOST2 to cos_btm2 force — fix black break)

- v0.1.6/0.1.7 forced LOST2 MAPJUMP to cos_btm2 and opened COS_BTM2 IFUW gates.
  That path is NOT how multi-disc CSR runs the break. On normal disc1 to disc2,
  GameMoment is never 0xa455, so LOST2 skips the cos_btm2 jump. Forcing the jump
  lands COS_BTM2 with the wrong moment: IFSW GM >= 0x202 hits RET immediately
  (black screen + music, no break menu).
- Restore pure CSR Disc 2 LOST2 + COS_BTM2 bytes (no force).
- Keep BLACKBGB Ask/DSKCG strips + disc-id SETBYTE and all 0.1.5 field Ask strips.
- Builder: single-disc-on-csr-v0.1.8 enabled; 0.1.7/0.1.6 disabled.

## 0.1.7 (disc1-to-disc2 break choreography on COS_BTM2)

- After LOST2 MAPJUMP to cos_btm2 (0.1.6), break still skipped: COS_BTM2 gates the
  scene on the same disc-id IFUW (18 20 00 00 55 a4). Multi-disc sets disc=2 after
  swap; single-disc stays disc=1 so the else branch skips to black+music.
- Clear COS_BTM2 IFUW else-jumps >= 0x08 (keep tiny +3 music taps).
- Includes 0.1.6 LOST2 force + 0.1.5 Ask strips.
- Builder: single-disc-on-csr-v0.1.7 enabled; 0.1.6 disabled.
- scripts/lzs.py: real FF7 LZS compress for size-safe FIELD rewrites.


## 0.1.6 (disc1-to-disc2 LOST2 break)

- Force CSR D2 LOST2 MAPJUMP to cos_btm2 (break scene) by clearing IFUW else-jump.
- Fixes missing disc2 open break / freeze-like hang on single-disc.
- Includes 0.1.5 residual Ask strips (CANON_2 post-Hojo, etc.).
- Builder: single-disc-on-csr-v0.1.6 enabled; 0.1.5 disabled.

## 0.1.5 (post-Hojo / field 744 freeze)

- Strip residual Ask-for-disc 2/3 (DSKCG) left after D2 field merge.
- CANON_2 (Sister Ray / post-Hojo) was the blocker into las0_1 (#744).
- Also stripped: COSMIN2, FRCYO, HYOU11, MDS5_W, SHPIN_3, SUBIN_1B, WHITEBG3.
- HYOU8_1 still has one disc-2 Ask (grew past ISO sector slot; follow-up).
- Builder: single-disc-on-csr-v0.1.5 enabled; 0.1.4 disabled.

## 0.1.4 (WHITE2 movie crawl fix)

- Restore movie-trimmed WHITE2 + LOSLAKE3 from 0.1.2 (pairs to 0).
- v0.1.3 pure CSR D2 WHITE2 reintroduced PMVIE+MOVIE that play wrong streams on D1
  (DuckStation MDEC/DMA crawl on field 643).
- Builder: single-disc-on-csr-v0.1.4 enabled; 0.1.3 disabled.

## 0.1.4 (CSR+ D2/D3 trims on single-disc D1 + Highwind SD)

- CSR+ disc1 layers (CSR repo): Hojo, COTA, endgame on Disc 1 with Single-disc.
- single-disc-on-highwind-v0.1.0: Highwind D2/D3 FIELD merge + SNOVA; endings auto.
- replace_file_within_sectors in scripts/psx_mode2_iso.py.

## 0.1.3 (endings as separate builder mod)

- **Ending credits pack (own mod):** `single-disc-endings-v0.1.0-part1` … `part7`
  (7 layers so each file stays under GitHub’s size limit). Puts ending/credits
  movies on the one Disc 1 image.
- **Not optional:** All 7 ending parts are hidden and **always auto-applied** with
  Single-disc on CSR (including CSR+). CompatibleBases also list Highwind for later.
  CSR manip movies remain separate and CSR-alone only.
- **CSR manip movies stay separate:** still only auto on **CSR alone** + Single-disc
  (not CSR+, not Highwind).
- DuckStation playtest of local ending image: lake + credits OK (user).
- Rebuild layers: `build_ending_credits_test_bin.py` then `build_ending_credits_layers.py`.
- Long credits may show messy name text where the lake movie shares disc space
  (known tradeoff). Map skips (e.g. first ending clip jump) stay intentional.

## 0.1.2 (tools note — endings CD recipe)

- Local ending burn recipe only (before builder multi-part pack).

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
