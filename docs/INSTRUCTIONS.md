# Task: run the RAM watcher script while you playtest

Watchpoint retry (with $ra fix) still never fired for the real
corruption -- memory was already corrupted at Ctrl+C despite no
watchpoint hit. Confirms the write is invisible to CPU watchpoints
(DMA, e.g. CD-ROM streaming into a bad/null destination), even
though the payload looks like readable text. Tightening polling to
try to catch it mid-transfer:

1. DuckStation: Settings → Advanced → enable "GDB Server" (port 19000).
2. In a terminal: `python3 scripts/gdb_ram_watch.py --no-watch --interval 0.02`
3. Load the game / continue play as normal in DuckStation.
4. Reproduce the freeze (JUNAIR, field 384, moment 1016, battle-return).
5. As soon as you see the freeze, **Ctrl+C** the terminal running the
   script — it writes `workspace/iso-extract/ram_watch_log.txt`.
6. Send me that file.
