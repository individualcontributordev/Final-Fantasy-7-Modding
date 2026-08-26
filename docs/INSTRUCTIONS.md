# Task: confirm CSR-only baseline, then RAM-watch the freeze

Core-only and core+movies both froze — bug is in the single-disc-on-csr
layer itself, not movies. One more check, then we debug live.

```
git pull --ff-only
cd ../Final-Fantasy-7-CSR && python3 scripts/build_csr_base_layers.py csr --version 0.14.2 --discs 1 && cd -
```

Playtest JUNAIR (field 384, moment 1016) on the plain CSR disc 1 build
(no single-disc layer): battle → return to field. Report freeze/no-freeze.

If it does NOT freeze (expected), open `ff7_d1_singledisc_core.bin` in
DuckStation with the debugger, set a write watchpoint on `0x00000000`,
trigger the same battle-return, and report the PC/call-stack/register
dump when it hits (or "skipped" if too fiddly).
