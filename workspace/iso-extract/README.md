# ISO extract — disposable working copies only

**Do not keep your only retail dump here.** CDmage auto-saves on import into
whatever image is open. Masters live in `workspace/pristine/`.

```
workspace/pristine/                 — never open in CDmage
  FINALFANTASY7_D1.bin … D3.bin (+ .cue)

workspace/iso-extract/              — working area (this folder)
  FINALFANTASY7_DN.bin (+ .cue)     — copy from pristine, then import stub here
  FIELD.BIN / FIELD.BIN.new
```

Same filename in both folders on purpose: prepare copies the vault; CDmage
patches the iso-extract file; the layer script diffs vault vs working copy.

```bash
python scripts/prepare_encounter_workspace.py --discs 1
# replace an existing working copy (only before patching):
python scripts/prepare_encounter_workspace.py --discs 1 --force
```

Full steps: `builder/WINDOWS-INSTRUCTIONS.md`.
