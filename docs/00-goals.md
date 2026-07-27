# Goals

PS1 Final Fantasy VII disc modding: change engine/field data, keep hardware playability, ship `ic-layer-v1` packs for https://individualcontributor.dev/builder/.

**In repo:** scripts, docs, layer JSON. **Not in repo:** disc images.

## Reading order

| Need | Go to |
|------|--------|
| Ship Field encounter rates | root [README.md](../README.md) |
| Encounter RE / RAM map | [01-encounter-system.md](01-encounter-system.md) |
| ISO / GZIPPS / Makou | [02-disc-format.md](02-disc-format.md), [04-workflow.md](04-workflow.md) |
| Tools | [03-environment-setup.md](03-environment-setup.md), [05-ghidra-guide.md](05-ghidra-guide.md) |
| Day-by-day RE trail | [findings/](findings/) |

## Principles

1. Console-first (emulator for iteration).
2. Pristine vault never opened in CDmage — copies / scripted inject only.
3. Smallest patch that works; document offsets in findings or mod `patches/`.
4. Publish only JSON under `builder/`.
