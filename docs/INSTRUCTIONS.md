# Task: identify source of corrupting write to 0x00000000

Screenshots show PC stuck at 0x80000088 (kernel exception-vector area)
with COP0_CAUSE=Reserved Instruction — the low-RAM jump table got
overwritten with raw file/text bytes. Write watchpoint on 0x00000000
never fired, so it's a DMA write (CD-ROM->RAM), not a CPU store.

In DuckStation, pause right at the freeze (same repro), open the
Memory panel, right-click near address 0x00000000, export/dump
0x00000000-0x00000800 to a file (any format: raw binary or the
panel's "Export" if available). Put it at
`workspace/iso-extract/corrupt_ram_dump.bin` and tell me it's there —
I'll grep `ff7_d1_singledisc_core.bin` for that byte sequence to find
which file/offset is being mis-targeted.
