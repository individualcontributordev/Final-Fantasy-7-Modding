# Pristine retail discs (gitignored binaries)

**Never open these in CDmage.** Import auto-saves the open file — that is what
wiped earlier “pristine” dumps and produced empty Encounter layers.

```
workspace/pristine/
  FINALFANTASY7_D1.bin  (+ .cue)
  FINALFANTASY7_D2.bin  (+ .cue)
  FINALFANTASY7_D3.bin  (+ .cue)
```

Working copies (same filenames) live under `workspace/iso-extract/`:

```bash
python scripts/prepare_encounter_workspace.py --discs 1
```

See `builder/WINDOWS-INSTRUCTIONS.md`.
