# ISO extract / disc images (gitignored except this README)

Put NTSC-U Disc 1–3 images and extracts here. Never commit game binaries.

```
workspace/iso-extract/
  FINALFANTASY7_D1.bin … D3.bin     (+ .cue)  — untouched retail
  FINALFANTASY7_DN_encounter.bin    (+ .cue)  — after Encounter stub reimport
  FIELD.BIN                                   — extract for the disc you are patching
  FIELD.BIN.new                               — from build_field_encounter_patch.py
```

Mods need a **separate layer per disc**. See `builder/WINDOWS-INSTRUCTIONS.md`.
