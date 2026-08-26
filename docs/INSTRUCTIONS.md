# Task: RAM-watch the JUNAIR freeze live

Confirmed: plain CSR disc 1 does NOT freeze. Bug is introduced by the
single-disc-on-csr layer itself.

```
git pull --ff-only
python3 mods/single-disc/scripts/build_singledisc_core_bin.py
printf 'FILE "ff7_d1_singledisc_core.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n' > workspace/iso-extract/ff7_d1_singledisc_core.cue
```

Open the resulting `.cue` in DuckStation with the debugger enabled
(Settings → Advanced → Show Debug Menu).

1. Debug → CPU Debugger → breakpoints/watchpoints panel.
2. Add a **write watchpoint on guest address `0x00000000`** (range
   `0x0000`–`0x1FFF` if supported).
3. JUNAIR (field 384, moment 1016): trigger a battle, let it finish,
   return to field.
4. When it hits, before resuming, capture: **PC**, **call stack**, and
   **all GPR registers** (especially whichever holds the target address
   — expect something like `0x80200000`).
5. Report PC + call stack + register dump, raw/untrimmed.
