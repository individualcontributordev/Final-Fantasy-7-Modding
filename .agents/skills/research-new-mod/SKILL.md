---
name: research-new-mod
description: >-
  End-to-end research and shipping process for new FF7 PSX disc mods in
  Final-Fantasy-7-Modding. Use when starting a new mod, scaffolding mods/,
  planning RE for WORLD.BIN or FIELD.BIN, or asking how to go from idea to
  builder pack.
---

# Research a new FF7 PSX mod

Full write-up: `docs/06-new-mod-research.md`. Follow that; this skill is the checklist.

## 1. Frame the mod

- One-sentence player-facing behavior
- **Makou vs Ghidra fork (do this first):**
  - Map data `FIELD/*.DAT` (Makou) → stop here; use **Final-Fantasy-7-CSR** skills `ship-makou-addon` or `ship-csr-plus-scene`
  - Engine binary `FIELD.BIN` / `WORLD.BIN` (Ghidra) → continue in this repo
- Which stack bases must it support? (`clean`, `csr-v…`, `highwind-v…`)

## 2. RE (Mac ↔ Windows)

- One atomic Windows task per turn (chat + `docs/windows-last-output.txt`)
- Align Ghidra VA with DuckStation before deep xref work (`docs/05-ghidra-guide.md`)
- Journal every useful result: `.agents/skills/record-findings`
- Promote confirmed facts into `docs/0N-*.md`

## 3. Patch + prove

- Smallest change; document offsets
- Decompress → patch `.dec` → recompress → inject (`docs/04-workflow.md`)
- Playtest with RAM watches that falsify “it boots so it works”
- Prefer **MiSTer PSX** after DuckStation for high-confidence logic checks (`docs/07-hardware-burn.md`)
- Freeze shipping bytes under `mods/<mod>/patches/`

## 4. Scaffold + ship

```
mods/<name>/VERSION
mods/<name>/README.md
mods/<name>/patches/
mods/<name>/scripts/    # when automating builds
```

- Diff patched `.bin` vs each stack base → `ic-layer-v1`
- Set `compatibleBases` + `exclusiveGroup` if variants conflict
- Prefer named presets + interactive CLI (see Field `density.py`)
- Commit `builder/` JSON only; push Pages CDN
- Skill for Field releases: `ship-field-encounters`

## Do not

- Open pristine vault discs in CDmage
- Invent free-form rate knobs when a few presets suffice
- Skip findings and rely on chat memory
- Publish without stating which base the layer was built against
- Leave a process breakthrough only in chat — run `evolve-re-process` so `docs/06` stays true

## Related

- Improve the loop after breakthroughs: `evolve-re-process`
- Journal facts: `record-findings`
- Ship Field packs: `ship-field-encounters`
