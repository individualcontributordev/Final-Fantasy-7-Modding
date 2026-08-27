# Task: run the RAM watcher script while you playtest

Confirmed: PC=0x80000080, Cause=0x428 (Reserved Instruction) — a write
to 0x0 clobbers the exception vectors, so the CPU crashes trying to
handle its own exception. First watchpoint hit was a false lead
(0x8003cde8/0x80042b00 = normal ExitCriticalSection syscall touching
the A0/B0/C0 table, not the bug). Script now auto-skips known-benign
writer PCs and keeps continuing until a real (non-skip-listed) hit:

1. DuckStation: Settings → Advanced → enable "GDB Server" (port 19000).
2. In a terminal: `python3 scripts/gdb_ram_watch.py --skip-benign-pc 0x8003cde8`
3. Load the game / continue play as normal in DuckStation.
4. Reproduce the freeze (JUNAIR, field 384, moment 1016, battle-return).
5. As soon as you see the freeze, **Ctrl+C** the terminal running the
   script — it writes `workspace/iso-extract/ram_watch_log.txt`.
6. Send me that file.
