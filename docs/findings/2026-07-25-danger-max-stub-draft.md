# In-place MAX-Danger stub draft (88-byte slot)

**Date:** 2026-07-25  
**Confidence:** likely  
**Related:** [danger-add-block-size](2026-07-25-danger-add-block-size.md)

## Slot

Overwrite `0x800ABB7C`–`0x800ABBD4` (88 bytes). Fall through to existing `jal increment_step_id`.

## Logic

```
entropy = COP0 Count
lure    = g_enemy_lure          # byte
if ((entropy & 0xff) < lure):   # higher lure → more FORCE
    g_danger = 0xFFFF
# else leave g_danger unchanged
# nop-pad to 0x800ABBD4
```

With lure≈16 → ~6% of checks FORCE; Away lower; Lure materia higher.

## Asm sketch (approx)

```
mfc0  v0, Count
lui   at, 0x8006
lbu   v1, 0x2f19(at)       ; g_enemy_lure
andi  v0, v0, 0xff
sltu  at, v0, v1           ; 1 if entropy < lure
beq   at, zero, skip
nop
lui   at, 0x8007
ori   v0, zero, 0xffff
sh    v0, 0x173c(at)       ; g_danger
skip:
; nops through 0x800ABBD0
```

Tune: use `lure << 1` etc. if default density feels wrong.

## Follow-ups

- [ ] Verify register safety vs later preempt path
- [ ] Assemble exact machine code + nop fill
- [ ] Apply + test in DuckStation
