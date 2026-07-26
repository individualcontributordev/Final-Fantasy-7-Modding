# Pristine retail discs (gitignored binaries)

**Never open these in CDmage for import.** CDmage can auto-save on import and
overwrite the file you opened — that is what produced empty Encounter layers.

```
workspace/pristine/
  FINALFANTASY7_D1.bin  (+ .cue)
  FINALFANTASY7_D2.bin  (+ .cue)
  FINALFANTASY7_D3.bin  (+ .cue)
```

Working copies live under `workspace/iso-extract/` — create them with:

```bash
python scripts/prepare_encounter_workspace.py --discs 1
```

See `builder/WINDOWS-INSTRUCTIONS.md`.
