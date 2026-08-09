# Task: Break on battle win-pose code (DuckStation)

## What we already learned (your screenshots)

Checked in repo (docs/normal *.png, docs/trains *.png):

- The **write** break on 80062D7C never hit (count stayed 0)
- That memory stayed **00 00** on both normal and train in those pauses
- The yellow arrow (current code) was in **main game code**, not the battle module

So we stop watching only that memory write. Next: break when **battle code runs** the win pose.

## What you need

- Same disc with **Fanfare Skip v0.1.4**
- DuckStation CPU debugger
- One **normal** fight (poses still play) is enough for this pass

## Breaks to add (Execute / CPU, not memory-write)

Clear the old write break on 80062D7C if it is still there.

Add **execute** breaks on:

| What | Address |
|------|---------|
| Win pose write (most important) | 800A54A0 |
| Pose gate just before that | 800A5484 |
| Victory queue (our stub - does it ever run?) | 800A2974 |
| Call into that queue | 800ABE4C |

Optional if none of those hit: 800A5250, 800A1CE0.

## Steps

1. Enter a normal battle.
2. Save state just before the last kill.
3. Enable the breaks above.
4. Kill the last enemy and let it run until a break hits **or** poses finish.
5. Screenshot the debugger when it stops (or note which address hit and the Hit Count).

## Write down

```
which breaks hit: (list addresses + hit counts)
did poses still play: yes/no
any stuck sound: yes/no
```

If **nothing** under 800A ever hits during the win pose, say so - then the battle code is loaded at a different place and we adjust.

## Do not

- Do not use old Fanfare Skip packs before 0.1.4
- Do not poke memory by hand
- Train fight not required this pass

## When done

Push screenshots under docs/ again or paste the list above in chat.
