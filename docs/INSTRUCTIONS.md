# Task: run the RAM watcher script while you playtest

Per-byte breakpoint (0x80034E54) was too slow (9000+ hits just loading).
Moved up to 0x800349ec, the return site after one whole compressed
chunk decompresses (fires once per chunk, not per byte) -- but it's a
shared routine used by menus/boot too, so we skip a batch of early
boring hits first, then stop on every hit after that so you can
Ctrl+C right at the freeze.

1. DuckStation: Settings → Advanced → enable "GDB Server" (port 19000).
2. In a terminal:
   `python3 scripts/gdb_ram_watch.py --break-pc 0x800349ec --skip-hits 300`
3. Load the game / continue play as normal in DuckStation.
4. Reproduce the freeze (JUNAIR, field 384, moment 1016, battle-return).
5. It'll silently skip the first 300 hits (boot/menu/field loads), then
   stop on the very next chunk-decompress after that -- likely still
   mid-load, not yet at the freeze. That's expected on this first run.
6. Send me `workspace/iso-extract/ram_watch_log.txt` either way -- I'll
   use the backtrace/registers to figure out how many more hits (or
   which higher-level caller) gets us to the actual freeze.
