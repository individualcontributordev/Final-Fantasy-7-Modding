# Findings journal

Lab notebook for this repo. Stable summaries: `docs/0N-*.md`. Shipped Field stub: `mods/field-random-encounters/`.

## Start here (engineers)

1. **Shipped behaviour** — `docs/01-encounter-system.md` + `mods/field-random-encounters/patches/README.md`
2. **How to rebuild layers** — root `README.md`
3. **ISO / FIELD.BIN pipeline** — `docs/02-disc-format.md`, `docs/04-workflow.md`
4. **This folder** — dated RE steps (Ghidra addresses, dead ends, playtests). Keep when diagnosing regressions; skip for “just ship a rate”.

**How to add:** copy `_template.md` → `YYYY-MM-DD-slug.md` → add a row below.

| Date | Slug | Summary | Confidence |
|------|------|---------|------------|
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
