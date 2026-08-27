# Task: run the RAM watcher script while you playtest

Confirmed: PC=0x80000080, Cause=0x428 (Reserved Instruction) — a DMA
write to 0x0 clobbers the exception vectors, so the CPU crashes trying
to handle its own exception. Script is now general-purpose: it captures
CPU regs, DMA channel regs, IRQ/timers, and an approximate call-stack
backtrace on every change, and auto-skips any HW port DuckStation's GDB
stub can't read (no more log spam). Reuse `--addr` for other bugs too:

1. DuckStation: Settings → Advanced → enable "GDB Server" (port 19000).
2. In a terminal: `python3 scripts/gdb_ram_watch.py`
3. Load the game / continue play as normal in DuckStation.
4. Reproduce the freeze (JUNAIR, field 384, moment 1016, battle-return).
5. As soon as you see the freeze, **Ctrl+C** the terminal running the
   script — it writes `workspace/iso-extract/ram_watch_log.txt`.
6. Send me that file.
