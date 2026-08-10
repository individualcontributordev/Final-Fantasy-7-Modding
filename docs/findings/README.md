# Findings journal

Lab notebook for this repo. Stable summaries: `docs/0N-*.md`. Shipped Field stub: `mods/field-random-encounters/`.

## Start here (engineers)

1. **Shipped behaviour** — `docs/01-encounter-system.md` + `mods/field-random-encounters/patches/README.md`
2. **How to rebuild layers** — root `README.md`
3. **ISO / FIELD.BIN pipeline** — `docs/02-disc-format.md`, `docs/04-workflow.md`
4. **PSX RAM map (queryable)** — `docs/reference/ff7-psx-memory/` (`query_memory.py`)
5. **This folder** — dated RE steps (Ghidra addresses, dead ends, playtests). Keep when diagnosing regressions; skip for “just ship a rate”.

**How to add:** copy `_template.md` → `YYYY-MM-DD-slug.md` → add a row below.

| Date | Slug | Summary | Confidence |
|------|------|---------|------------|
| 2026-08-09 | [win-transition-fn-800a1158](2026-08-09-win-transition-fn-800a1158.md) | win_transition handoff live: 16F4 s1=FFFF, jal 801B0000 ra=800A1734 | confirmed |
| 2026-08-09 | [batres-801b0000-victory-entry](2026-08-09-batres-801b0000-victory-entry.md) | BATRES@801B0000: entry from win_transition; first jal 800A6000 x10 | confirmed |
| 2026-08-09 | [batres-late-jals-stuck-tone](2026-08-09-batres-late-jals-stuck-tone.md) | freeze = quiet FAN2 only; stub-only OK (fanfare still plays) | confirmed |
| 2026-08-09 | [fanfare-skip-015-gap-ceremony-still-plays](2026-08-09-fanfare-skip-015-gap-ceremony-still-plays.md) | 0.1.5: Ghidra batres_victory; wait s4=0x31; anim type 4 | confirmed |
| 2026-08-09 | [fanfare-skip-duckstation-compare](2026-08-09-fanfare-skip-duckstation-compare.md) | F83C6 writes = BATTLE.X 0x154C/1584; next exec 800A1500 | in-progress |
| 2026-08-08 | [battle-fanfare-mod-feasibility](2026-08-08-battle-fanfare-mod-feasibility.md) | Victory Skip v0.1.0: force BATTLE.X bit0x20 at 22 sites | shipped |
| 2026-08-09 | [fanfare-skip-train-sub-verify](2026-08-09-fanfare-skip-train-sub-verify.md) | Fanfare Skip v0.1.3 vs train + UJUNON/sub fields (static) | verify |
| 2026-08-07 | [ending-credits-cd-playtest-pass](2026-08-07-ending-credits-cd-playtest-pass.md) | User: ending test bin lake+credits OK (CSR/SD fields kept) | confirmed |
| 2026-08-07 | [post-manip-movies-todo-triage](2026-08-07-post-manip-movies-todo-triage.md) | After manip-movies: drop intentional CSR/SD skips; keep seed+LBA fixes | confirmed |
| 2026-08-07 | [sd-core-play-skips-vs-ending](2026-08-07-sd-core-play-skips-vs-ending.md) | After SD core: report JMPF/Play skips; fix ending streams not unskip | confirmed |
| 2026-08-07 | [csr-base-vs-d3-ending-skips](2026-08-07-csr-base-vs-d3-ending-skips.md) | D1 CSR base has no end skips; CSR D3 does; SD core brings LAS4_0 skip | confirmed |
| 2026-08-07 | [csr-d3-ending-movie-jumps](2026-08-07-csr-d3-ending-movie-jumps.md) | CSR D3 JMPF-skips ENDING01 + LASTMAP early play; absent on ending-v7 | confirmed |
| 2026-08-07 | [last-fields-csr-d3-vs-ending-v7](2026-08-07-last-fields-csr-d3-vs-ending-v7.md) | LAS0 match CSR D3; LASTMAP/LAS4_* movie ops differ (SD skips LAS4_2/3) | confirmed |
| 2026-08-07 | [ending-overwrite-csr-manip-audit](2026-08-07-ending-overwrite-csr-manip-audit.md) | Ending LBA alias vs manip seeds; LAST4_3 restore | confirmed |
| 2026-08-07 | [ending-credits-test-inject](2026-08-07-ending-credits-test-inject.md) | Oversize DS test: D3 ENDING01/2E/3E into D1 MOVIE_ID ids 25/26/29 | confirmed |
| 2026-08-07 | [ending-credits-d3-fit-on-d1](2026-08-07-ending-credits-d3-fit-on-d1.md) | D3 ENDING2E ~156 MiB will not fit on current single-disc D1 (~77 MiB free) | confirmed |
| 2026-08-06 | [field-collisions-2026-08-06](field-collisions-2026-08-06/README.md) | Tool + batch: all 10 D1/D2 CSR stems are real script collisions (not pad-only) | confirmed |
| 2026-08-06 | [del1-d2-pristine-vs-csr-opcodes](2026-08-06-del1-d2-pristine-vs-csr-opcodes.md) | DEL1 D2: scripts identical; CSR only strips dialog padding (−444) | confirmed |
| 2026-08-04 | [single-disc-csr-manip-movies-v010-seed](2026-08-04-single-disc-csr-manip-movies-v010-seed.md) | Seed movie pack: 4 files id-slot overwrite |
| 2026-08-04 | [single-disc-rename-from-no-disc-swap](2026-08-04-single-disc-rename-from-no-disc-swap.md) | Rename no-disc-swap → single-disc |
| 2026-08-04 | [single-disc-csrplus-fmv-deduce-manip-movies](2026-08-04-single-disc-csrplus-fmv-deduce-manip-movies.md) | COTA+endgame CSR+ diffs: only small endgame movies for CSR-alone |
| 2026-08-04 | [single-disc-on-csr-build-status](2026-08-04-single-disc-on-csr-build-status.md) | CSR single-disc pack v0.1.1 partial; BLACKBGB Makou pending |
| 2026-08-04 | [single-disc-ship-csrplus-highwind-first](2026-08-04-single-disc-ship-csrplus-highwind-first.md) | Ship CSR+/HW single-disc first; defer CSR manip movies |
| 2026-08-04 | [single-disc-bases-csr-highwind-only](2026-08-04-single-disc-bases-csr-highwind-only.md) | single-disc CSR/HW only; Clean retired |
| 2026-08-04 | [single-disc-imgburn-edc-warn-console-ok](2026-08-04-single-disc-imgburn-edc-warn-console-ok.md) | ImgBurn EDC warn but console play OK v0.1.1 |
| 2026-08-04 | [single-disc-csr-manip-movies-pack-split](2026-08-04-single-disc-csr-manip-movies-pack-split.md) | CSR manip FMV optional pack; not auto-off with CSR+ |
| 2026-08-04 | [single-disc-fr-e-blin70-movie-trims](2026-08-04-single-disc-fr-e-blin70-movie-trims.md) | fr_e #347 + blin70_4 #269 Set+Play trims |
| 2026-08-04 | [single-disc-d2d3-movie-trims-unblock](2026-08-04-single-disc-d2d3-movie-trims-unblock.md) | D2/D3 Set+Play trims unblocked playtest |
| 2026-08-04 | [single-disc-load-save-asks-disc2](2026-08-04-single-disc-load-save-asks-disc2.md) | Load save asks disc 2: save disc id vs field Ask |
| 2026-08-03 | [single-disc-field-movie-scan](2026-08-03-single-disc-field-movie-scan.md) | D1 PMVIE scan Tier1 crawl candidates |
| 2026-08-03 | [single-disc-ioslake3-missing-fmv](2026-08-03-single-disc-ioslake3-missing-fmv.md) | ioslake3 missing FMV (Bugenhagen idle); not freeze |
| 2026-08-03 | [single-disc-console-boot-pass](2026-08-03-single-disc-console-boot-pass.md) | single-disc burned CD: title/new game/first field PASS |
| 2026-08-03 | [single-disc-imgburn-verify-pass](2026-08-03-single-disc-imgburn-verify-pass.md) | single-disc CD-R ImgBurn verify PASS; console pending |
| 2026-08-03 | [single-disc-fmv-wait-vs-stream](2026-08-03-single-disc-fmv-wait-vs-stream.md) | Wrong FMV often ends early; wait/manip time may still match |
| 2026-08-03 | [single-disc-combined-ds-pass](2026-08-03-single-disc-combined-ds-pass.md) | Ask+SNOVA combined D1 work bin DS PASS |
| 2026-08-03 | [single-disc-supernova-ds-pass](2026-08-03-single-disc-supernova-ds-pass.md) | Supernova DS PASS after BATTLE.X LBA remap v3 |
| 2026-08-03 | [single-disc-snova-injector](2026-08-03-single-disc-snova-injector.md) | D3 SNOVA/ inject onto D1; offline OK; DS playtest pending |
| 2026-08-03 | [single-disc-makou-ask-ds-pass](2026-08-03-single-disc-makou-ask-ds-pass.md) | Makou all Ask-for-disc removed; DuckStation PASS; console untested | confirmed |
| 2026-08-03 | [single-disc-field-movie-dskcg-stub](2026-08-03-single-disc-field-movie-dskcg-stub.md) | FIELD DSKCG+MOVIE handlers; jr ra stub plan; tool under mods/single-disc | likely |
| 2026-08-03 | [single-disc-full-run-scope](2026-08-03-single-disc-full-run-scope.md) | No ship until full-run safe; SNOVA/movies/Asks all required | confirmed |
| 2026-08-02 | [single-disc-blackbgb-ask-skip-proto](2026-08-02-single-disc-blackbgb-ask-skip-proto.md) | blackbgb: Ask skipped via Goto OK; gate Bit OFF accidentally skipped — fix | confirmed |
| 2026-08-02 | [single-disc-blackbgb-hub-branches](2026-08-02-single-disc-blackbgb-hub-branches.md) | blackbgb S0: 4 asks → las0_1#744 / lost2#634; save bits 5/2 + Var[13][0] | confirmed |
| 2026-08-02 | [single-disc-ask-for-disc-inventory](2026-08-02-single-disc-ask-for-disc-inventory.md) | D1 Ask for disc: 19 hits in blackbgb/e/3 only; hub=blackbgb #103 | confirmed |
| 2026-08-02 | [single-disc-disc-change-pristine](2026-08-02-single-disc-disc-change-pristine.md) | D1: DISK0001 + MOVIE/DISKn.LZS; swap = Makou Ask for disc N then map jump | confirmed |
| 2026-08-02 | [disc-cross-compare](2026-08-02-disc-cross-compare.md) | D1/D2/D3: code+FIELD identical; diffs are FMV + disc-id; single-disc single-disc plausible without full movies | confirmed |
| 2026-07-30 | [verify-built-disc-stacking](2026-07-30-verify-built-disc-stacking.md) | Zip verify: match APPLIED ids; ignore EDC/ECC + base bytes addons overwrite | confirmed |
| 2026-07-30 | [world-light-runtime-verify](2026-07-30-world-light-runtime-verify.md) | Builder zip PASS; stub live; danger 0/FFFF; 0x40 not FORCE; DS/CE watches | confirmed |
| 2026-07-28 | [world-light-dense-feel](2026-07-28-world-light-dense-feel.md) | Light≈Standard short walk; Dense clearly higher; ship all three | likely |
| 2026-07-28 | [world-force-playtest](2026-07-28-world-force-playtest.md) | Standard stub applied; fewer fights than vanilla on DS | likely |
| 2026-07-28 | [world-lure-factor](2026-07-28-world-lure-factor.md) | world_lure_factor @ 0x800B7B54; g_enemy_lure DAT_80062f19 | confirmed |
| 2026-07-28 | [world-danger](2026-07-28-world-danger.md) | g_world_danger @ 0x80116284; += then WorldRand < danger>>8 | confirmed |
| 2026-07-28 | [world-encounter-caller](2026-07-28-world-encounter-caller.md) | RA before battle → FUN_800b7c7c (jal @ 0x800B81C4) | confirmed |
| 2026-07-28 | [worldrand-break-partial](2026-07-28-worldrand-break-partial.md) | DS break hits WorldRand; need ra register values | partial |
| 2026-07-28 | [worldrand-xrefs-reject](2026-07-28-worldrand-xrefs-reject.md) | abb24/a21b4/b0250 not encounter; use DS break on WorldRand | confirmed |
| 2026-07-28 | [world-4000-scalar-miss](2026-07-28-world-4000-scalar-miss.md) | 0x4000 hits are GTE/flags; encounter likely uses sll 14 | likely |
| 2026-07-28 | [worldrand](2026-07-28-worldrand.md) | WorldRand @ 0x800ADFC0; index wrap 0x208; ~20 xrefs | confirmed |
| 2026-07-28 | [worldrand-candidate](2026-07-28-worldrand-candidate.md) | FUN_800adfc0 sole non-seed caller of WorldScrambleRand | likely |
| 2026-07-28 | [worldscramblerand](2026-07-28-worldscramblerand.md) | WorldScrambleRand @ 0x800ADE30; index 0x8010AE58; buf 0x8010AE5C | confirmed |
| 2026-07-28 | [worldrand-mislabel](2026-07-28-worldrand-mislabel.md) | 0x800C4148 is NOT WorldRand (scratch/GPU; 0x208 false positive) | confirmed |
| 2026-07-28 | [worldseedrand](2026-07-28-worldseedrand.md) | WorldSeedRand @ 0x800ADEA8; lui/ori 0x5D588B65 | confirmed |
| 2026-07-28 | [worldseedrand-scalar-miss](2026-07-28-worldseedrand-scalar-miss.md) | 0x5D588B65 full scalar 0 hits; try lui/ori halves | confirmed |
| 2026-07-28 | [world-bin-load-base](2026-07-28-world-bin-load-base.md) | WORLD.BIN @ 0x800A0000 (same slot as FIELD) | confirmed |
| 2026-07-28 | [world-bin-extract](2026-07-28-world-bin-extract.md) | WORLD.BIN 66715 → .dec 164032; GZIPPS OK | confirmed |
| 2026-07-27 | [world-map-encounter-plan](2026-07-27-world-map-encounter-plan.md) | WORLD.BIN target; WorldRand + separate Danger; Field stub does not apply | planned |
| 2026-07-25 | [g-formation](2026-07-25-g-formation.md) | DAT_80071c20 → g_formation via lbu @ 0x800ABA38 | confirmed |
| 2026-07-25 | [increment-formation](2026-07-25-increment-formation.md) | FUN_800aba34; Formation @ 0x80071C20; table lookup | confirmed |
| 2026-07-25 | [g-step-fraction](2026-07-25-g-step-fraction.md) | DAT_8009c6d8 → g_step_fraction via lbu @ 0x800ABAB4 | confirmed |
| 2026-07-25 | [encounter-check-renamed](2026-07-25-encounter-check-renamed.md) | FUN_800aba70 → encounter_check @ 0x800ABA70 | confirmed |
| 2026-07-25 | [encounter-check-entry](2026-07-25-encounter-check-entry.md) | True entry FUN_800aba70 @ 0x800ABA70 | confirmed |
| 2026-07-25 | [danger-increment](2026-07-25-danger-increment.md) | g_danger += via div/mflo @ 0x800ABB7C–ABBD0 | confirmed |
| 2026-07-25 | [g-danger-rename](2026-07-25-g-danger-rename.md) | DAT_8007173c → g_danger via lhu @ 0x800ABC1C | confirmed |
| 2026-07-25 | [encounter-check](2026-07-25-encounter-check.md) | Dual jal + Danger compare; entry likely wrong | confirmed |
| 2026-07-25 | [increment-step-id-xrefs](2026-07-25-increment-step-id-xrefs.md) | 2 jal callers @ 0x800ABBD4, 0x800ABC10 | confirmed |
| 2026-07-25 | [align-ghidra-duckstation-base](2026-07-25-align-ghidra-duckstation-base.md) | Ghidra+DuckStation aligned; FIELD @ 0x800A0000 | confirmed |
| 2026-07-25 | [increment-step-id-complete](2026-07-25-increment-step-id-complete.md) | Full fn; table via 0x800E0638; load base likely 0x800A0000 | confirmed |
| 2026-07-25 | [increment-step-id](2026-07-25-increment-step-id.md) | increment_step_id @ ~0x8000B9C8; lui 0x800a addressing | confirmed |
| 2026-07-25 | [field-dec-addr-search](2026-07-25-field-dec-addr-search.md) | .dec: RNG @ 0x40638; no abs StepID ptr; 3× 0xC540 | confirmed |
| 2026-07-25 | [search-ran-on-compressed-field-bin](2026-07-25-search-ran-on-compressed-field-bin.md) | Search used FIELD.BIN not .dec → 0 hits | confirmed |
| 2026-07-25 | [ghidra-no-stepid-scalars](2026-07-25-ghidra-no-stepid-scalars.md) | Scalars 0x9c540 / 0xc540: no hits | confirmed |
| 2026-07-25 | [ghidra-zero-xrefs-rng-table](2026-07-25-ghidra-zero-xrefs-rng-table.md) | RNG table @ 0x80040638 has 0 xrefs; use scalar search | confirmed |
| 2026-07-25 | [field-bin-extract](2026-07-25-field-bin-extract.md) | FIELD.BIN 85435 → .dec 264008; RNG @ 0x40638 | confirmed |
| 2026-07-25 | [encounter-rng-architecture](2026-07-25-encounter-rng-architecture.md) | FIELD.BIN owns encounter RNG; Makou edits DAT only | confirmed |
| 2026-07-25 | [makou-iso-save-path](2026-07-25-makou-iso-save-path.md) | Makou → ff7tk pack/updateFieldBin flow | confirmed |
| 2026-07-25 | [duckstation-accurate-settings](2026-07-25-duckstation-accurate-settings.md) | Safe Mode + testing profile for hardware-like behavior | confirmed |
| 2026-07-25 | [force-stub-dual-jal-ok](2026-07-25-force-stub-dual-jal-ok.md) | Delay nop + second jal intact | confirmed |
| 2026-07-25 | [cdmage-cannot-write-test-bin](2026-07-25-cdmage-cannot-write-test-bin.md) | Save failed: cannot write test.bin (locked?) | confirmed |
| 2026-07-25 | [cdmage-save-options-pending](2026-07-25-cdmage-save-options-pending.md) | CDmage Save options shown; finalize then DS test | likely |
| 2026-07-25 | [cdmage-pad-shorter-import](2026-07-25-cdmage-pad-shorter-import.md) | Shorter import: Yes pad zeros (−80) | likely |
| 2026-07-25 | [cdmage-field-bin-path](2026-07-25-cdmage-field-bin-path.md) | Engine FIELD.BIN is FIELD/FIELD.BIN; restore pristine | confirmed |
| 2026-07-25 | [cdmage-wrong-field-bin](2026-07-25-cdmage-wrong-field-bin.md) | Truncate = FIELD/FIELD.BIN not root engine | confirmed |
| 2026-07-25 | [cdmage-import-truncate-warning](2026-07-25-cdmage-import-truncate-warning.md) | Truncate warning = wrong file/target; do not OK | confirmed |
| 2026-07-25 | [force-stub-compressed](2026-07-25-force-stub-compressed.md) | FIELD.BIN.new 85355 (−80 vs stock) | confirmed |
| 2026-07-25 | [force-stub-export-verified](2026-07-25-force-stub-export-verified.md) | xxd confirms stub @ 0xBB7C in .dec.patched | confirmed |
| 2026-07-25 | [patch-log-force-stub](2026-07-25-patch-log-force-stub.md) | FORCE stub patch log (VA/file offset) | confirmed |
| 2026-07-25 | [force-stub-complete-ghidra](2026-07-25-force-stub-complete-ghidra.md) | FORCE stub + jal restore verified in Ghidra | confirmed |
| 2026-07-25 | [force-stub-patched-jal-clobber](2026-07-25-force-stub-patched-jal-clobber.md) | Stub OK; restore jal @ 0x800ABBD4 | confirmed |
| 2026-07-25 | [playtest-preempt-flag](2026-07-25-playtest-preempt-flag.md) | Preempt flag still 4 then 0 | confirmed |
| 2026-07-25 | [playtest-lure-poke](2026-07-25-playtest-lure-poke.md) | lure 1=none, 16=normal, 64=alot | confirmed |
| 2026-07-25 | [lure-playtest-deferred](2026-07-25-lure-playtest-deferred.md) | No materia yet; poke g_enemy_lure in RAM | confirmed |
| 2026-07-25 | [playtest-rcnt2-sparse](2026-07-25-playtest-rcnt2-sparse.md) | RCnt2 stub: sparse encounters; Offset wrap OK | confirmed |
| 2026-07-25 | [export-stale-mfc0](2026-07-25-export-stale-mfc0.md) | .dec.patched still mfc0; patch file on disk | confirmed |
| 2026-07-25 | [rcnt2-stub-patched-ghidra](2026-07-25-rcnt2-stub-patched-ghidra.md) | RCnt2 stub + jal verified in Listing | confirmed |
| 2026-07-25 | [playtest-always-force](2026-07-25-playtest-always-force.md) | mfc0 Count invalid on PSX; always FORCE | confirmed |
| 2026-07-25 | [danger-max-stub-draft](2026-07-25-danger-max-stub-draft.md) | RCnt2 FORCE stub (fix always-FORCE) | likely |
| 2026-07-25 | [dat-71e38-71e3c-xrefs](2026-07-25-dat-71e38-71e3c-xrefs.md) | 71e38/71e3c live; no Danger=0 retarget | confirmed |
| 2026-07-25 | [map-setup-danger0-candidates](2026-07-25-map-setup-danger0-candidates.md) | Retarget rejected; stub always writes Danger | confirmed |
| 2026-07-25 | [dat-8009fe8c-xrefs](2026-07-25-dat-8009fe8c-xrefs.md) | fe8c heavily read; cannot steal clear for Danger=0 | confirmed |
| 2026-07-25 | [field-map-init-danger0-hook](2026-07-25-field-map-init-danger0-hook.md) | fe8c steal rejected; need map-setup slot | confirmed |
| 2026-07-25 | [fun-800a14d8-scratchpad](2026-07-25-fun-800a14d8-scratchpad.md) | 0x1F800000 scratchpad; use mfc0 Count for entropy | confirmed |
| 2026-07-25 | [entropy-1f80-hits](2026-07-25-entropy-1f80-hits.md) | Many lui 0x1f80; check FUN_800a14d8 for RCnt | confirmed |
| 2026-07-25 | [entropy-search-empty](2026-07-25-entropy-search-empty.md) | No 0x1f801110/120 or mfc0 in FIELD | confirmed |
| 2026-07-25 | [g-enemy-lure-xrefs](2026-07-25-g-enemy-lure-xrefs.md) | Only READ in FIELD; writers elsewhere | confirmed |
| 2026-07-25 | [g-enemy-lure](2026-07-25-g-enemy-lure.md) | DAT_80062f19 → g_enemy_lure (byte); mult/srl12 compare | confirmed |
| 2026-07-25 | [danger-add-block-size](2026-07-25-danger-add-block-size.md) | Danger += is 88 bytes @ 0x800ABB7C–ABBD4; in-place OK | confirmed |
| 2026-07-25 | [not-a-cave-e0700](2026-07-25-not-a-cave-e0700.md) | 0x800E0700 is RNG table; prefer in-place Danger+= patch | confirmed |
| 2026-07-25 | [field-map-init-renamed](2026-07-25-field-map-init-renamed.md) | FUN_800ba534 → field_map_init @ 0x800BA534 | confirmed |
| 2026-07-25 | [field-map-setup](2026-07-25-field-map-setup.md) | LAB_800a1dc8 setup; FUN_800ba534 init candidate | likely |
| 2026-07-25 | [fun-800a2d5c](2026-07-25-fun-800a2d5c.md) | Texture/VRAM upload from buffer; not map enter | confirmed |
| 2026-07-25 | [fun-800aa870](2026-07-25-fun-800aa870.md) | Entity setup loop; not map load | confirmed |
| 2026-07-25 | [field-main-loop](2026-07-25-field-main-loop.md) | FUN_800a16cc @ 0x800A16CC; post-battle Danger clear | confirmed |
| 2026-07-25 | [danger-clear-site](2026-07-25-danger-clear-site.md) | g_danger=0 @ 0x800A1C70 in FUN_800a16cc (post-battle) | likely |
| 2026-07-25 | [g-danger-xrefs](2026-07-25-g-danger-xrefs.md) | 4 xrefs; clear @ 0x800A1C70; += @ ABBC0/ABBD0 | confirmed |
| 2026-07-25 | [patch-target-field-load-reseed](2026-07-25-patch-target-field-load-reseed.md) | Danger=0 on field enter; per-check RNG may set Danger MAX | likely |

## Index by topic

### Encounter RNG
- [2026-07-25-encounter-rng-architecture](2026-07-25-encounter-rng-architecture.md)
- [2026-07-25-patch-target-field-load-reseed](2026-07-25-patch-target-field-load-reseed.md)
- [2026-07-25-patch-log-force-stub](2026-07-25-patch-log-force-stub.md)
- [2026-07-25-playtest-rcnt2-sparse](2026-07-25-playtest-rcnt2-sparse.md)

### Tools & ISO
- [2026-07-25-duckstation-accurate-settings](2026-07-25-duckstation-accurate-settings.md)
- [2026-07-25-makou-iso-save-path](2026-07-25-makou-iso-save-path.md)
- [2026-07-25-field-bin-extract](2026-07-25-field-bin-extract.md)
- [2026-07-25-cdmage-field-bin-path](2026-07-25-cdmage-field-bin-path.md)
