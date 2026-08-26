# Task: log DMA transfers to catch the write to 0x0

Watchpoint on 0x0 is confirmed to cover all RAM mirrors (DuckStation
dedupes them) and still never fires — so this is NOT a CPU store, it's
a DMA write (CD-ROM/GPU/SPU DMA writing straight to RAM, which CPU
watchpoints can't catch). Need DMA logging instead:

1. Settings → Advanced → enable debug/trace logging, turn on the
   **DMA** log channel (and CDROM if separate) at Debug/Trace level.
2. Reproduce the freeze (JUNAIR, field 384, moment 1016, battle-return).
3. Save/export the log (or screenshot the last ~30 lines before the
   freeze) and put it at `workspace/iso-extract/dma_log.txt`.
4. Tell me it's there — looking for a DMA transfer whose destination
   address is 0x00000000 or very close to it.
