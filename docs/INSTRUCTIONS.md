# Task: Break on victory-start PC (from your shots)

## What your two shots showed

| File | Moment | **pc** | Notes |
|------|--------|--------|-------|
| docs/victory-pose-start-debugger.png | You think win pose **starts** | **800D3098** | Best hook so far |
| docs/victory-pose-mid-anim-debugger.png | Mid animations | 800C63AC | Looks like color/GPU unpack — less useful |

### Gold from the start shot (registers)

| Reg | Value | Meaning |
|-----|-------|---------|
| pc | 800D3098 | Code running as poses begin |
| ra | 8003CF98 | Return into lower/system code |
| s4 | **800F83C6** | **Exit Battle Status** address (same as memory map) |
| s1 | 800F83E0 | Near battle-end block |
| s5 | 800F836C | Near battle frame field |
| gp | 80062D44 | Near battle globals (RNG/input block) |

Disassembly at that PC touches **80051568** (global frame counter) then branches — a small check/helper, not the full pose AI by itself. Still the right **time** to freeze.

## Do this next (one execute break)

1. Clear old 800A… execute breaks (world map spam).
2. Add **one** execute break: **800D3098**
3. Optional write break: **800F83C6** (1 byte) — value 1 = Victory per memory map.
4. Normal fight, save before last kill.
5. Kill last enemy.

When **800D3098** hits:

- Screenshot debugger (full registers + stack).
- Note **Hit Count**.
- Write down **ra** and the top few stack addresses.
- Read byte at **800F83C6** (should often be 1 or becoming 1).

If it hits **every battle frame** forever, say so (too hot).
If it hits **once** near pose start, perfect.
If it never hits, pause by eye at pose start again and send the new pc.

## Write down

```
800D3098 hit: yes/no  count: ?
ra: ........
800F83C6: ..
stack top 3: ...
```

## Do not

- Do not re-enable 800A54A0 / 800A5484 / 800A2974 execute breaks
- Mid-anim break on 800C63AC not needed this pass

800D3098 is hitting every frame
see screenshots for other data
when the exp and rewards page opens that break 800F83C6 no longer hits