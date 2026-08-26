# Task: run the RAM watcher script while you playtest

Watchpoint on 0x0 is confirmed to cover all RAM mirrors and still never
fires, so it's a DMA write, not a CPU store. Built a script that polls
RAM 0x0 directly over DuckStation's GDB server instead of relying on
its (limited) debugger UI:

1. DuckStation: Settings → Advanced → enable "GDB Server" (port 19000).
2. In a terminal: `python3 scripts/gdb_ram_watch.py`
3. Load the game / continue play as normal in DuckStation.
4. Reproduce the freeze (JUNAIR, field 384, moment 1016, battle-return).
5. As soon as you see the freeze, **Ctrl+C** the terminal running the
   script — it writes `workspace/iso-extract/ram_watch_log.txt`.
6. Send me that file.
