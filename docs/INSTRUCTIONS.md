# Task: dump RAM at the freeze for exact byte comparison

Screenshots confirmed PC stuck at 0x80000088 (kernel exception-vector
area) with COP0_CAUSE=Reserved Instruction — low RAM got overwritten
with garbage. Manual hex transcription from screenshots didn't match
the built disc (too error-prone). Need an exact dump instead:

1. Reproduce the freeze in DuckStation (JUNAIR field 384, battle-return).
2. Menu: **Debug → Dump RAM...** and save to
   `workspace/iso-extract/corrupt_ram_dump.bin`.
3. Tell me it's there — I'll diff it against a known-good RAM dump /
   grep the built disc to find which file/offset is mis-targeted.
