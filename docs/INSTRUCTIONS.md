No pending ops task right now.

See `docs/findings/2026-08-23-blackbgb-splice-lost2-lzs-fix-verified.md` for
the resolved BLACKBGB D1->D2 hang + LOST2 corruption fixes (both confirmed
on real hardware).

## Reference: BLACKBGB manual-edit splice

The automated DSKCG (ask-for-disc) removal for BLACKBGB still hangs the
D1->D2 transition even after the bit-exact LZS encoder fix, for reasons not
yet root-caused (see follow-ups in the finding above). The workaround is to
splice a known-working manually-edited `FIELD/BLACKBGB.DAT` (edited in Makou
Reactor with the DSKCG ops removed, confirmed working on hardware) straight
into the build, bypassing our own re-encoder for this field:

```
python3 mods/single-disc/scripts/extract_field_from_bin.py path/to/your-working-manual-edit.bin --field BLACKBGB -o workspace/iso-extract/BLACKBGB.manual.dat
python3 mods/single-disc/scripts/build_work_bin.py -o OUT.bin --blackbgb-manual-bin workspace/iso-extract/BLACKBGB.manual.dat
```

`--blackbgb-manual-bin` accepts either a full disc `.bin` or a raw extracted
`.DAT` (auto-detected by whether the file size is a multiple of 2352).
