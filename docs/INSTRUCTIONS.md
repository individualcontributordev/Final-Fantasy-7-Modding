# Task: run the RAM watcher script while you playtest

MADR watchpoint never fired (stub likely can't watch 0x1F80xxxx MMIO).
Pivoting per docs/findings/2026-08-26-junair-...-freeze.md: DuckStation's
own debug log already named the exact guest PC issuing the bad write
(0x80034E54, writes to 0x80200000 which wraps onto 0x0). Set an
*execution* breakpoint there instead of a data watchpoint.

1. DuckStation: Settings → Advanced → enable "GDB Server" (port 19000).
2. In a terminal: `python3 scripts/gdb_ram_watch.py --break-pc 0x80034E54`
3. Load the game / continue play as normal in DuckStation.
4. Reproduce the freeze (JUNAIR, field 384, moment 1016, battle-return).
5. It should stop automatically when that PC executes (before the
   freeze) and write `workspace/iso-extract/ram_watch_log.txt`. If it
   doesn't stop within a minute or two of returning from battle,
   Ctrl+C the terminal instead — it'll still write the log.
6. Send me that file.
