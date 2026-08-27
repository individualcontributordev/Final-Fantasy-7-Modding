# Task: run the RAM watcher script while you playtest

Polling confirmed corrupted bytes at 0x0 are readable text fragments
(menu/dialog strings), not a DMA fill pattern -- likely a CPU store
with a bad pointer after all. Retrying the hardware watchpoint (now
with the $ra skip-list fix) to catch the exact instruction.

1. DuckStation: Settings → Advanced → enable "GDB Server" (port 19000).
2. In a terminal: `python3 scripts/gdb_ram_watch.py --skip-benign-pc 0x8003cde8`
3. Load the game / continue play as normal in DuckStation.
4. Reproduce the freeze (JUNAIR, field 384, moment 1016, battle-return).
5. As soon as you see the freeze, **Ctrl+C** the terminal running the
   script — it writes `workspace/iso-extract/ram_watch_log.txt`.
6. Send me that file.
