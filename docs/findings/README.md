# Findings journal

Dated research notes for **FF7 PSX disc modding**. Stable guides live in
`docs/0N-*.md`; this folder is the lab notebook.

**How to add an entry:** copy `_template.md` → `YYYY-MM-DD-slug.md` → update the index below.

| Date | Slug | Summary | Confidence |
|------|------|---------|------------|
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
| 2026-07-25 | [patch-target-field-load-reseed](2026-07-25-patch-target-field-load-reseed.md) | Encounter topic: planned field-load RNG reseed | likely |

## Index by topic

### Encounter RNG
- [2026-07-25-encounter-rng-architecture](2026-07-25-encounter-rng-architecture.md)
- [2026-07-25-patch-target-field-load-reseed](2026-07-25-patch-target-field-load-reseed.md)
- [2026-07-25-ghidra-zero-xrefs-rng-table](2026-07-25-ghidra-zero-xrefs-rng-table.md)
- [2026-07-25-ghidra-no-stepid-scalars](2026-07-25-ghidra-no-stepid-scalars.md)
- [2026-07-25-field-dec-addr-search](2026-07-25-field-dec-addr-search.md)
- [2026-07-25-increment-step-id](2026-07-25-increment-step-id.md)
- [2026-07-25-increment-step-id-complete](2026-07-25-increment-step-id-complete.md)

### Tools & environment
- [2026-07-25-duckstation-accurate-settings](2026-07-25-duckstation-accurate-settings.md)

### Disc / ISO
- [2026-07-25-makou-iso-save-path](2026-07-25-makou-iso-save-path.md)
- [2026-07-25-field-bin-extract](2026-07-25-field-bin-extract.md)
- [2026-07-25-search-ran-on-compressed-field-bin](2026-07-25-search-ran-on-compressed-field-bin.md)
