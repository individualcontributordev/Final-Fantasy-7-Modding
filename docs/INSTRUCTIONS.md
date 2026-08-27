# Task: run the RAM watcher script while you playtest

0.02s polling still saw nothing between last-good and corrupted (26s
apart) -- the write is a single instant DMA burst, not a slow loop.
New plan: the DMA *destination* write is invisible to watchpoints,
but the CPU store that *programs* the DMA channel's MADR (source
address reg) to point there is not. Watching CD-ROM DMA channel 3's
MADR (0x1F8010C0) instead of 0x0 -- if it's set to ~0x0, that's the
setup code corrupting things.

1. DuckStation: Settings → Advanced → enable "GDB Server" (port 19000).
2. In a terminal: `python3 scripts/gdb_ram_watch.py --addr 0x1F8010C0 --watch-len 4`
3. Load the game / continue play as normal in DuckStation.
4. Reproduce the freeze (JUNAIR, field 384, moment 1016, battle-return).
5. As soon as you see the freeze, **Ctrl+C** the terminal running the
   script — it writes `workspace/iso-extract/ram_watch_log.txt`.
6. Send me that file.
