# Task: run the RAM watcher script while you playtest

Confirmed again: PC=0x80000088, Cause=0x428 (Reserved Instruction) in
the corrupted vector — but the CPU write watchpoint never fired for
it (only skip-listed ExitCriticalSection hits fired). Likely a DMA
burst (not a CPU store) does the corrupting write, which CPU-only
watchpoints can't catch. Switching to polling/diffing instead, which
catches changes regardless of what wrote them:

1. DuckStation: Settings → Advanced → enable "GDB Server" (port 19000).
2. In a terminal: `python3 scripts/gdb_ram_watch.py --no-watch`
3. Load the game / continue play as normal in DuckStation.
4. Reproduce the freeze (JUNAIR, field 384, moment 1016, battle-return).
5. As soon as you see the freeze, **Ctrl+C** the terminal running the
   script — it writes `workspace/iso-extract/ram_watch_log.txt`.
6. Send me that file.
