# ISO extract / disc images (gitignored except this README)

Put NTSC-U Disc 1 images and extracts here. Never commit game binaries.

```
workspace/iso-extract/
  FINALFANTASY7_D1.bin              (+ .cue)  — untouched retail
  FINALFANTASY7_D1_encounter.bin    (+ .cue)  — after Encounter stub reimport
  FIELD.BIN                                   — extracted from pristine
  FIELD.BIN.new                               — from build_field_encounter_patch.py
```

See `builder/WINDOWS-INSTRUCTIONS.md`. Keep names consistent across extract → patch → diff → verify.
