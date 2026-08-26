# Task: confirm CSR-only baseline, then RAM-watch the freeze

Core-only and core+movies both froze — bug is in the single-disc-on-csr
layer itself, not movies. One more check, then we debug live.

```
git pull --ff-only
python3 ../Final-Fantasy-7-CSR/scripts/apply_layer.py ../Final-Fantasy-7-CSR/pristine/FINALFANTASY7_D1.bin ../Final-Fantasy-7-CSR/builder/csr-v0.14.2/layers/disc1.layer.json -o workspace/iso-extract/ff7_d1_csr_only.bin
printf 'FILE "ff7_d1_csr_only.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > workspace/iso-extract/ff7_d1_csr_only.cue
```

Playtest JUNAIR (field 384, moment 1016) on the plain CSR disc 1 build
(no single-disc layer): battle → return to field. Report freeze/no-freeze.

If it does NOT freeze (expected), open `ff7_d1_singledisc_core.bin` in
DuckStation with the debugger, set a write watchpoint on `0x00000000`,
trigger the same battle-return, and report the PC/call-stack/register
dump when it hits (or "skipped" if too fiddly).
