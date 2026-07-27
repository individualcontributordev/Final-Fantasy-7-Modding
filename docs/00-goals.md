# Goals

PS1 Final Fantasy VII disc modding: change engine/field data, keep hardware playability, ship stackable `ic-layer-v1` packs for https://individualcontributor.dev/builder/.

**In repo:** scripts, docs, layer JSON. **Not in repo:** disc images, `.bin` dumps.

## Reading order

| Need | Go to |
|------|--------|
| Ship Field encounter rates | `mods/field-random-encounters/` + `builder/WINDOWS-INSTRUCTIONS.md` |
| Encounter RE / RAM map | `docs/01-encounter-system.md` |
| ISO / GZIPPS / Makou | `docs/02-disc-format.md`, `docs/04-workflow.md` |
| Tools | `docs/03-environment-setup.md`, `docs/05-ghidra-guide.md` |
| Day-by-day RE trail | `docs/findings/` |

## Principles

1. Console-first (emulator for iteration).
2. Pristine vault never opened in CDmage — work on copies / scripted inject.
3. Smallest patch that works; document offsets in findings or mod `patches/`.
4. Publish only JSON under `builder/` (Pages CDN for the main-site builder).
