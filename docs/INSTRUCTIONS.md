# Task: bisect JUNAIR freeze

```
git pull --ff-only
python3 mods/single-disc/scripts/build_singledisc_core_bin.py
printf 'FILE "ff7_d1_singledisc_core.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > workspace/iso-extract/ff7_d1_singledisc_core.cue
python3 mods/single-disc/scripts/build_playtest_bin.py
```

Playtest JUNAIR (field 384, moment 1016) on both resulting discs:
battle → return to field. Report freeze/no-freeze for each.
