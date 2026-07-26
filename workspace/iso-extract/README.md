# ISO extract — disposable working copies only

**Do not keep your only retail dump here.** CDmage can auto-save on import and
overwrite the open image. Masters live in `workspace/pristine/`.

```
workspace/pristine/                         — never open for import
  FINALFANTASY7_D1.bin … D3.bin (+ .cue)

workspace/iso-extract/                      — working area (this folder)
  FINALFANTASY7_DN.bin (+ .cue)             — copy from pristine (script)
  FINALFANTASY7_DN_encounter.bin (+ .cue)   — Save As + FIELD.BIN.new import
  FIELD.BIN / FIELD.BIN.new                 — extract + stub pipeline
```

Refresh a working copy before each disc:

```bash
python scripts/prepare_encounter_workspace.py --discs 1
# replace an existing working copy:
python scripts/prepare_encounter_workspace.py --discs 1 --force
```

Full steps: `builder/WINDOWS-INSTRUCTIONS.md`.
