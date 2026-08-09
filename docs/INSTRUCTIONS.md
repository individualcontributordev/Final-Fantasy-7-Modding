# Task: Catch the first write to exit-battle status

## What we learned from your last shots

| Shot | Result |
|------|--------|
| before last / after last / mid anim | Execute **800D3098** Hit Count 53 → 54 → 76 |
| Your note | 800D3098 hits **every frame** |
| read value.png | At **800F83C6** the byte was **00** (not Victory yet) |
| Your note | Once EXP/rewards is open, **800F83C6** break goes quiet |

### Verdict

**Turn OFF execute break 800D3098.**

That address is a **3D/GTE render loop** (runs the whole fight). It is **not** the win-pose controller. Landing on it at "pose start" before was coincidence.

800F83C6 is still useful as a **write** watch: it can stay 0 through early win anim, then get written in the handoff into rewards.

## Setup

1. Delete execute break on **800D3098**.
2. Delete any leftover **800A…** execute breaks.
3. Add **one** breakpoint:
   - Type: **Write** (memory), not execute
   - Address: **800F83C6**
   - Size: **1 byte**
4. Optional (kill timing only): write break on **800F85AC** (enemy 1 HP). Turn it off after the last enemy dies if it is too noisy.

## Run

1. Normal battle, Fanfare Skip 0.1.4.
2. Save state before last kill.
3. Arm the **800F83C6 write** break.
4. Kill the last enemy.
5. When the debugger **first** stops on that write, screenshot and note:

```
first F83C6 write:
  pc: ........
  ra: ........
  value at 800F83C6: ..
  hit count: 1 (or ?)
  game moment: (poses? rewards? still fighting?)
```

6. If it never breaks between kill and rewards, say so.
7. If the first break is only on the rewards screen, also **manual pause** at the first win-pose frame (D3098 off) and screenshot pc.

## Do not

- Do not leave **800D3098** execute on
- Do not use old **800A54A0**-style execute breaks

## When done

Push screenshots under docs/ or paste the pc/ra/value block in chat.
