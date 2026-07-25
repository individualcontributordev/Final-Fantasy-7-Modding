# Findings journal

Dated research notes for **FF7 PSX disc modding**. Stable guides live in
`docs/0N-*.md`; this folder is the lab notebook.

**How to add an entry:** copy `_template.md` → `YYYY-MM-DD-slug.md` → update the index below.

| Date | Slug | Summary | Confidence |
|------|------|---------|------------|
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

### Tools & environment
- [2026-07-25-duckstation-accurate-settings](2026-07-25-duckstation-accurate-settings.md)

### Disc / ISO
- [2026-07-25-makou-iso-save-path](2026-07-25-makou-iso-save-path.md)
- [2026-07-25-field-bin-extract](2026-07-25-field-bin-extract.md)
