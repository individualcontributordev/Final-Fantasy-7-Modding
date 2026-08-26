# Task: catch the corrupting write via mirrored watchpoints

RAM dump confirms 0x0 holds decompressed text garbage (field dialogue
fragments), not raw disc bytes — so it's a wrong-destination-pointer
bug, not a bad byte copy. Your earlier watchpoint on 0x00000000 alone
likely missed it because PSX RAM is mirrored at 0x00000000 (KUSEG),
0x80000000 (KSEG0), and 0xA0000000 (KSEG1) — same physical page.

1. Reproduce up to just before the freeze (JUNAIR, field 384, moment
   1016, battle almost over).
2. Add **three write watchpoints**: 0x00000000, 0x80000000, 0xA0000000
   (small range, e.g. first 0x800 bytes of each).
3. Finish the battle, return to field.
4. When one hits, capture: PC, call stack, and all GPR registers
   (especially whichever register holds the destination address).
5. Report which watchpoint fired + full register/PC dump.
