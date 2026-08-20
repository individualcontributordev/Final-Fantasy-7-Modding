## 0.1.3 — 2026-08-20

**Rebuilt from scratch** with automated field-merge tooling, replacing the
old hand-audited/hardcoded field lists (`csr-field-disc-prefer.txt`,
`csr-d2d3-field-merge-on-d1.md`) that had drifted out of sync with the
0.1.2/0.1.2.3 shipped bytes.

- **9-field "rework" merge** (`merge_rework_fields.py`): per-slot verdict
  table for the fields where CSR D1/D2 genuinely diverge on the same
  entity/slot — BLACKBGB, COS_BTM, COS_BTM2, DEL1, JUNAIR2 (whole CSR D1),
  LOST2 (whole CSR D2), and true per-slot splices for BUGIN1A, NIVGATE,
  RCKTIN2.
- **66-field safe bulk merge** (`merge_safe_fields.py`, new): programmatically
  discovers every other field CSR only really edited (vs pristine) on one
  non-D1 disc and wholesale-swaps it in — 61 D2-only fields (e.g. CONVIL_1/2,
  FSHIP_1-4/22-25, JUNONE2/22/7, RCKTIN3/5/6, TRNAD_*, ZMIND1-3, etc.) + 4
  D3-only fields (LAS4_0/2/4, LASTMAP) + RCKTIN7 (re-classified from
  "collision" to safe auto-merge: CSR D2 is a pure superset of CSR D1's
  slots for this field). Of the ~776 fields present on 2+ discs, 548 had
  zero CSR edits on any disc and 163 already matched the D1 base, so only
  these 66 needed an actual merge.
- **DSKCG ("Ask for disc") removal**: automated via `field_dat_write.py`
  splicer instead of manual Makou Reactor edits — 19/19 ops removed
  (BLACKBGB: 4, BLACKBGE: 1, BLACKBG3: 14), same count as prior manual
  passes.
- **SNOVA D3→D1 inject** unchanged (`inject_snova_d3_to_d1.py`): copies
  Supernova files onto D1 and remaps BATTLE.X's 17 hardcoded LBAs.
- Confirmed the LOST2/COS_BTM2 disc-break gate needs no extra patch this
  time: LOSIN2 unconditionally sets the Game Moment break flag as part of
  its story cutscene (not gated on a disc-swap check), so the merged CSR D2
  LOST2 fires the break-scene MAPJUMP on its own.
- Every merged/spliced field verified to parse cleanly via `field_dat.py`
  and byte-match its intended CSR source. Layer diffed fresh against
  pristine Disc 1 (152,740 records, ~5.95MB changed).
- Movies/endings packs (manip-movies v0.1.4, endings v0.1.0 parts 1-7) are
  unchanged and still auto-apply with Single-disc on CSR.
- **Manifest fixup (post-release)**: the v0.1.2 whole-bin-diff changeover
  (`58fd5cd`) had removed manip-movies v0.1.4's `autoIncludeWhen` entirely
  and pointed endings v0.1.0 parts 1-7 at a disabled sentinel, so the claim
  above was not actually true in the builder until this fixup. Also
  disabled the stale `single-disc-v0.1.2-part2..10` whole-bin-diff
  auto-includes left over from that same changeover, which had been
  stacking v0.1.2 bytes on top of this v0.1.3 layer. Both manip-movies
  v0.1.4 and endings v0.1.0 parts 1-7 are now restored to auto-apply with
  `single-disc-on-csr`, and `verify_builder_config.py` confirms the full
  9-addon stack (base + mod layer + manip-movies + 7 endings parts,
  4,360,412 total records) applies cleanly.

## 0.1.2.3 — 2026-08-19

- **Field 637 (CANONON.MOV) audio flicker fix**: `single-disc-on-csr` layer
  carried 3 stray records (offsets 298608536/298608637/298608639 in
  `MINT/MOVIE_ID.BIN`) that reverted `single-disc-csr-manip-movies-v0.1.4`'s
  correct Form2 engine lengths for MOVIE_ID rows 47 (CANONON, field 637) and
  52 (CANONHT2/Hojo) back to their pre-manip (wrong) ISO-byte-size values,
  right after manip-movies set them. This regression previously escaped
  detection because it was only checked by reading the manip-movies layer in
  isolation, not the full applied stack. Removed the 3 offending records —
  both rows now keep their correct Form2 values (row 47: 17,190,624; row 52:
  5,977,824) through the full build.
- **Field 643 (WHITE2/Cosmo Canyon) missing CSR changes fix**: the CSR base's
  real Disc-2 story/script edit to `FIELD/WHITE2.DAT` (a `JMPF` bypass added
  before the FADE in the `cl` entity's post-movie script, entity slot `cl/31`)
  was dropped when the 0.1.4 movie-crawl fix rewrote this script from the
  *pristine* (unmerged) version instead of the CSR-D2-merged version. Field
  637's cannon movie was correctly identified as unrelated to field 643/639
  (waterfall) — see finding doc. Rebuilt `cl/31`'s script bytes from the CSR
  Disc-2 version with `PMVIE`/`MOVIE` opcodes stripped (preserving the
  movie-crawl-avoidance behavior) while keeping the CSR `JMPF` edit intact.
  Field 643's story/script CSR changes are restored; still does not play the
  waterfall movie (correct — see field 639 in the finding doc).

## 0.1.2-rollback — 2026-08-17

**Rolled back from v0.1.40 to v0.1.2 (last known working version)**

- User tested manually-built bin matching v0.1.2 pattern — complete and working
- Only known issue: Movie audio flickers (ending + loslake1 field 637)
- v0.1.3 through v0.1.40 introduced regressions in disc 1→2 transition
- Rebuilding v0.1.2 from analysis of working bin

**Build pattern:**
- LOST2: CSR D2 (break scene IFUW else=0xA4 works as-is)
- DEL1: CSR D1
- LOSIN2: CSR D1
- CANON_2: CSR D2
- BLACKBGB/E/3: DSKCG removed (19 operations deleted)
- SNOVA: Disc 3 → Disc 1
- Movies: manip-movies v0.1.2 (cumulative seed + LBA alias)

Next: Fix movie audio flickers, then publish v0.1.41

## 0.1.34 (disc-break scene: LOSIN2 bit + COS ASK)

## 0.1.35 — 2026-08-13

- **FAIL retire v0.1.34** (LOSIN2 BITON / COS open — no music, no break in playtest).
- **v0.1.35** auto delta: LOST2 CSR D2 init — when bank3/0x84 bit4 is OFF, fail IFUB into
  **AKAO2 + MUSIC** instead of silent RET (1-byte E 0x1c to 0x24). No COS force.
- Badge / core id still single-disc-on-csr-v0.1.33 with version **0.1.35**.


- Pure CSR D2 LOST2 never MAPJUMPs COS_BTM2 after LOSIN2: LOSIN2 sets GM 0xa455
  and BITOFFs bank3/0x84#4, so LOST2 init RETs (no break, no music path).
- Multi-disc still does DSKCG then forest; the gated COS_BTM2 ASK is the CSR
  "break scene" on that flag path when bit4 is on (LOSINN sets it on multi).
- Fix (hidden auto):
  1) LOSIN2: BITOFF 84#4 -> BITON 84#4 (same 4 bytes)
  2) LOST2: pure CSR D2
  3) COS_BTM2: IFSW fail lands on break + large IFUW a455 else cleared so ASK runs
- Badge v0.1.34; pack single-disc-on-csr-v0.1.34 auto with Single-disc.

## 0.1.33 (repo purge)

- Deleted retired single-disc pack dirs/layers (0.1.1-0.1.25, ref pack, old movies).
- Core layer lives under single-disc-on-csr-v0.1.33 only (no shared v0.1.24 id).
- Path FMVs remain one hidden auto (v0.1.26). Old fanfare/victory versions removed.

## 0.1.33 (note)

- CSR field-ref internal pack disabled (core already pure CSR D2 LOST2/COS scripts).
- Path-engine remains uiHidden auto for Highwind path FMVs only — not required for D1→2 break.

## 0.1.33 (CSR D1/D2 reference reset)

- Deleted spiral Gate1 packs/scripts (0.1.27–0.1.32 forces on LOST2/COS_BTM2).
- Break-path fields now match CSR multi-disc reference:
  - LOSIN2 = CSR Disc 1
  - LOST2 = pure CSR Disc 2
  - COS_BTM2 = pure CSR Disc 2
  - BLACKBGB = Ask-stripped (no DSKCG), same as prior good core
- Player pack id **single-disc-on-csr-v0.1.33** (badge matches id).
- Autos: path-engine v0.1.26; ref pack restores pure D2 LOST2/COS if needed.
- Core layer bytes still shared from builder/single-disc-on-csr-v0.1.24/.

## 0.1.32 (Gate1 COS_BTM2 actually reaches break ASK)
- Pack id cleanup: player id single-disc-on-csr-v0.1.32 matches badge (no more version X with id v0.1.24 on one APPLIED line).

- Playtest v0.1.31 APPLIED stack correct (movies+24+26+31+endings) but no break.
  LOST2 did MAPJUMP #526; COS_BTM2 still never ran the break ASK.
- Root cause (FFRTT): IFSW before break used E=0x05 so fail landed on RET @0x72,
  not break IFUW @0x73. Changing only C (>= to ==) still RET on a455.
- Fix on COS_BTM2 (from pure CSR D2):
  1) IFSW GM 0x0202 before SETBYTE/RET: C== and **E 0x05->0x06** (fail->0x73)
  2) Large IFUW a455 else-jumps (>=0x08) -> 0 (v0.1.7 style) so break body runs
  3) Keep LOST2 a455->MJ526 and Ask BLACKBGB from 0.1.31
- Stack: movies + 0.1.24 + 0.1.26 + 0.1.31 + **0.1.32** (27-30 still disabled).

## 0.1.31 (Gate1 disc-break: LOST2 to COS_BTM2)

- Playtest v0.1.30: transition OK but no break scene and no music on #634.
  Pure CSR D2 LOST2 with LOSIN2 GM=0xa455 RETs (no MUSIC, no MAPJUMP #526).
  COS_BTM2 also RET on GM>=0x0202 before the break ASK block.
- Fix (minimal, same-length):
  1) LOST2 init IFUW !=0xa455 fail else 0x12 to 0x13 lands MAPJUMP #526
  2) COS_BTM2 IFSW GM>=0x0202 to GM==0x0202 so a455 reaches break ASK/music
  3) Keep Ask-stripped BLACKBGB (no DSKCG / no BITON84)
- Cleanup: disable auto for v0.1.27-0.1.30. Stack is movies + core 0.1.24
  + path 0.1.26 + 0.1.31 only.
- Hidden pack single-disc-on-csr-v0.1.31; badge v0.1.31.

## 0.1.30 (restore known-good disc-break fields)

- v0.1.27–0.1.29 broke D1→D2 again: AKAO2/IFUW forces and BLACKBGB BITON 0x84#4
  caused black/glitch transition (same failure as v0.1.6/0.1.7 → fixed in 0.1.8).
- Restore v0.1.8/0.1.9 path: Ask-stripped BLACKBGB (no BITON84), pure CSR D2
  LOST2 + COS_BTM2 (IFUW else stays 0x0B; no AKAO2 JMPF).
- Hidden pack single-disc-on-csr-v0.1.30 auto with Single-disc.

## 0.1.29 (disc-break gate bit on BLACKBGB)

- D1→D2 still skipped break scene and music: LOST2 only MAPJUMPs COS_BTM2 (#526)
  when bank3[0x84] bit4 is set and GM==0xa455. LOSIN2 sets GM 0xa455 but BITOFFs
  that bit; with bit clear LOST2 init RETs (no music, no break). Forcing COS_BTM2
  via IFUW else=0 (v0.1.28) blacks the scene (v0.1.8 finding).
- Fix: BLACKBGB before each MAPJUMP #634 sets BITON 82308404 (same encoding as
  LOSINN). Same-length swap: WAIT04+WAIT08+BITON89 → BITON84/4+BITON89+JMPF0.
  Restore pure CSR D2 LOST2 + COS_BTM2 (undo 0.1.27/28 script forces).
- Hidden pack single-disc-on-csr-v0.1.29 auto with Single-disc.

## 0.1.28 (disc-break scene LOST2 to COS_BTM2)

- After D1 to D2 transition, game went straight to LOST2 #634 forest with no break
  scene and bad music. Pure CSR D2 LOST2 only MAPJUMPs cos_btm2 when IFUW
  GM==0xa455 falls through; else +0x0B skips break. v0.1.6 force was lost later.
- Restore: LOST2 IFUW else 0x0B→0 (always MAPJUMP #526 cos_btm2). COS_BTM2 clear
  large disc-id IFUW else-jumps (v0.1.7). Hidden pack v0.1.28.
  Superseded by 0.1.29 (force blacked the break).

## 0.1.27 (LOST2 #634 music after disc break)

- No music on field 634 after D1 to D2 break. CSR D2 LOST2 runs AKAO2 cmd 0x9A
  (resume music) then MUSIC. Multi-disc has BLACKBGB DSKCG first; single-disc
  Ask-strip removes DSKCG so resume does nothing and music stays silent.
- Fix: JMPF over the two AKAO2 0x9A ops in LOST2 init (keep CSR D2 otherwise).
- Hidden pack single-disc-on-csr-v0.1.27 auto with Single-disc.

## 0.1.26 (path-engine under 80min + cache bust)

- Still would not load after 0.1.25b: sticky browser layer cache on id@version
  0.1.25, and path streams past 80:00:00 MSF (DuckStation CD limit).
- New pack id single-disc-on-csr-v0.1.26 (auto, uiHidden): MOVIE_ID in-place at
  LBA 126959; reuse PARASHOT@OPENINGE + CANONHT2@CAR_1209; append only
  CANONHT0/1/H3F/H1P; image ends ~79:10. Disable auto for 0.1.25.
- Player-facing Single-disc badge v0.1.26.

## 0.1.25b (MOVIE_ID in-place — DuckStation boot)

- Disc would not load: DuckStation Logical seek to [80:52:34] failed.
  v0.1.25 had relocated MINT/MOVIE_ID.BIN to EOF LBA 363784 (past ~80min CD).
- Rebuild path-engine layer: grow MOVIE_ID at original LBA 126959 (1220 bytes).
- Keep PMVIE remap + CSR D2 FSHIP_24/BLIN66_6.

## 0.1.25 (D2 engine movie IDs — PARASHOT on MD8_5; FSHIP_24/BLIN66_6 CSR D2)

- MD8_5 (#731) glitched: D2 field scripts use engine MOVIE_ID indices. On D2 mid 53 is
  PARASHOT; D1 table had only 54 rows so mids 55/59 were out of range and 50–53 still
  meant early-game D1 streams. v0.1.24 injected file payloads but patched MOVIE_ID by
  LBA (wrong rows).
- Fix: grow MOVIE_ID to 61 rows; install D2 path streams at new ids 54–59; remap
  FSHIP_12/MD8_5/MD8_52 PMVIE (53→58 PARASHOT, FSHIP_12→54–57, MD8_52→59).
- FSHIP_24 (#71) and BLIN66_6 (#255): restore pure CSR Disc 2 (CSR trims; D1 was pristine).

## 0.1.24 (path FMVs after manip-movies — PARASHOT/NRCRL unique LBAs)

- PARASHOT missing + MD8_5 glitch when manip-movies applied after SD core:
  shared movie LBAs clobbered path injects.
- Builder apply order: manip-movies then single-disc-on-csr.
- Pack bin-diffed vs CSR+movies; path FMVs force-append at unique EOF LBAs
  (PARASHOT, METEOFIX, METEOSKY, NRCRL, NRCRLB).
- JAIROFAL/CANONON alias preserved. FSHIP_12/MD8_52 CSR scripts restored.

## 0.1.23 (FSHIP_12 PARASHOT — Cloud Highwind deck FMV)

- User: CSR D2 movie PARASHOT positions Cloud; CSR+single-disc cut/broken.
- FSHIP_12 (#67) ad/3 on CSR: PMVIE 59 PARASHOT, 50 METEOFIX, 51 METEOSKY then MAPJUMP.
- Single-disc had stripped those Set+Play ops (movie trim).
- Restore CSR FSHIP_12.DAT + inject D2 PARASHOT/METEOFIX/METEOSKY into D1 mids 59/50/51.
- Keeps MD8_52 NRCRL (0.1.22) and MD8_5 NRCRLB (0.1.21). Prefer path fields unchanged.

## 0.1.22 (MD8_52 NRCRL — Cloud position FMV)

- CSR multi-disc MD8_52 (#779) plays PMVIE mid=52 (NRCRL.MOV) then MAPJUMP FSHIP_25 (#72).
- Single-disc had stripped Set+Play (movie trim); jump ran with no FMV — Cloud mis-positioned vs CSR D2.
- Restore CSR MD8_52.DAT (Set+Play) and inject D2 NRCRL into D1 mid52 (MTNVL2 slot, grow).
- Keeps 0.1.21 NRCRLB mid53 (MD8_5). Prefer fields LOSIN2/LOST2/CANON_2/BLACKBGB unchanged.

## 0.1.21 (MD8_5 mid53 NRCRLB — Highwind 71 to 67 to 731)

- Path without COTA/Hojo skip: FSHIP_24 (#71) to FSHIP_12 (#67) to MD8_5 (#731).
- MAPJUMP 67 to 731 was already correct; MD8_5 plays PMVIE mid=53.
- On multi-disc D2 mid53 = NRCRLB.MOV; on D1 mid53 = NIVLSFS.MOV (wrong stream).
- Inject D2 NRCRLB Form2 into D1 NIVLSFS slot + MOVIE_ID eng size/aux.
- Does not change LOSIN2 / LOST2 / CANON_2 / BLACKBGB / WHITE2 / FSHIP FIELD vs 0.1.20.

# Single-disc changelog

Newest at top.

## 0.1.20 (CANON_2 Hojo field — undo bad DSKCG strip in AKAO)

- Report: CSR + Single-disc only; CANON_2 (#741) fully glitched as soon as the
  Hojo field loads (disc-3 path not reachable).
- MIM/BSX match CSR D2. All script slots and texts match CSR D2.
- Only 14 bytes differ: inside the **AKAO** block, seven times `0e 03` became
  `10 00`. That is the old Ask/DSKCG strip pattern (NOP DSKCG disc 3) applied as
  a raw byte search, not as a real field opcode.
- CSR D2 CANON_2 has **zero** DSKCG/ASK opcodes; those `0e 03` bytes are music
  data. Corrupting them glitches the field on load.
- Restore pure CSR Disc 2 CANON_2.DAT. Prefer: CANON_2.DAT d2 (keep pure D2;
  do not raw-strip 0e0x inside AKAO).
- Keeps 0.1.9 LOSIN2 D1 + LOST2/COS_BTM2 D2 break path.
- Builder: single-disc-on-csr-v0.1.20 enabled; older main packs off.

## 0.1.9 (LOSIN2 end-of-D1 must stay CSR D1)

- Field #632 LOSIN2 is end of disc 1 (before BLACKBGB disc-2 ask/break hub).
- Blind D2 FIELD merge put CSR Disc 2 LOSIN2 on the one-disc image.
- CSR D1 LOSIN2 init sets GameMoment 0xa455 (break sentinel) then party goes to
  BLACKBGB. CSR D2 LOSIN2 never writes 0xa455 — so LOST2/COS_BTM2 break gates
  never open (black + regular D2 music).
- Restore CSR D1 LOSIN2. Keep CSR D2 LOST2 + COS_BTM2 (0.1.8) and BLACKBGB
  Ask/DSKCG strips.
- Prefer list: LOSIN2.DAT d1 (do not overwrite with D2 on future merges).
- Builder: single-disc-on-csr-v0.1.9 enabled; 0.1.8 and older main packs off.

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
