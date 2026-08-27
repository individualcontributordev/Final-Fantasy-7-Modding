# Task: run the RAM watcher script while you playtest

Breakpoint at 0x80034E54 hit immediately -- it's a decompressor's
per-byte store loop (`sb $v0,($t1)`), $t1=dest ptr, called constantly
for normal (safe) decompression too. First hit had $t1=0x801a0000,
nowhere near the danger zone. Need to skip hits until $t1 (r9) climbs
near 0x80200000, using the new --break-reg auto-skip.

1. DuckStation: Settings → Advanced → enable "GDB Server" (port 19000).
2. In a terminal:
   `python3 scripts/gdb_ram_watch.py --break-pc 0x80034E54 --break-reg r9 --break-reg-min 0x801f0000`
3. Load the game / continue play as normal in DuckStation.
4. Reproduce the freeze (JUNAIR, field 384, moment 1016, battle-return).
5. It should auto-skip harmless hits and only stop once r9 nears the
   wrap boundary, writing `workspace/iso-extract/ram_watch_log.txt`.
   If it never stops and the game freezes anyway, Ctrl+C instead.
6. Send me that file.
