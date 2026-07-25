# Findings journal

Dated research notes for **FF7 PSX disc modding**. Stable guides live in
`docs/0N-*.md`; this folder is the lab notebook.

**How to add an entry:** copy `_template.md` → `YYYY-MM-DD-slug.md` → update the index below.

| Date | Slug | Summary | Confidence |
|------|------|---------|------------|
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
| 2026-07-25 | [danger-max-stub-draft](2026-07-25-danger-max-stub-draft.md) | In-place mfc0+lure FORCE stub for 88-byte slot | likely |
| 2026-07-25 | [map-setup-danger0-candidates](2026-07-25-map-setup-danger0-candidates.md) | Retarget 71e38/71e3c sh-zero to g_danger | likely |
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
- [2026-07-25-ghidra-zero-xrefs-rng-table](2026-07-25-ghidra-zero-xrefs-rng-table.md)
- [2026-07-25-ghidra-no-stepid-scalars](2026-07-25-ghidra-no-stepid-scalars.md)
- [2026-07-25-field-dec-addr-search](2026-07-25-field-dec-addr-search.md)
- [2026-07-25-increment-step-id](2026-07-25-increment-step-id.md)
- [2026-07-25-increment-step-id-complete](2026-07-25-increment-step-id-complete.md)
- [2026-07-25-increment-step-id-xrefs](2026-07-25-increment-step-id-xrefs.md)
- [2026-07-25-encounter-check](2026-07-25-encounter-check.md)
- [2026-07-25-encounter-check-entry](2026-07-25-encounter-check-entry.md)
- [2026-07-25-g-danger-rename](2026-07-25-g-danger-rename.md)
- [2026-07-25-danger-increment](2026-07-25-danger-increment.md)

### Tools & environment
- [2026-07-25-duckstation-accurate-settings](2026-07-25-duckstation-accurate-settings.md)

### Disc / ISO
- [2026-07-25-makou-iso-save-path](2026-07-25-makou-iso-save-path.md)
- [2026-07-25-field-bin-extract](2026-07-25-field-bin-extract.md)
- [2026-07-25-search-ran-on-compressed-field-bin](2026-07-25-search-ran-on-compressed-field-bin.md)
