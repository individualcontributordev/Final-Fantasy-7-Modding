# Task: Trace the F83C6 flag function (win transition)

## What we learned (your 4 post-kill shots)

Write BP on **800F83C6** is solved:

| When | What happens |
|------|----------------|
| Fight start / HUD loading | A few writes (init) |
| HUD fully up, mid-fight | **Silent** |
| After final kill | **Exactly 4 hits**, then silent through world map |

All 4 post-kill hits are the **same BATTLE.X function**:

| Shot | pc | Meaning |
|------|-----|---------|
| 1st | **800A1550** | After store that **clears** bits 0x22 (`andi … 0xFFDD`) |
| 2nd | **800A1588** | After store that **sets bit 0x20** |
| 3rd | **800A1550** | Clear path again; RAM halfword **0x0061** |
| 4th | **800A1588** | Set 0x20 again |

- **s5 = 800F83C6** every time
- **ra = 800A1408** every time
- Matches **BATTLE.X** file offsets **0x154C** / **0x1584** on disk

So: this is real battle overlay code at `800A15xx` (not the bad old 54A0 guess, not the D3098 renderer).

Early stops before HUD = **same function initializing flags**. Expected. Ignore those.

## Setup (new)

1. **Remove** write break on **800F83C6** (optional: leave off).
2. **Remove** any **800D3098** execute break.
3. Add execute breaks (code, not memory write):
   - **800A1500** (main — start here)
   - Optional: **800A1540**, **800A1580**
4. Enter a normal battle with Fanfare Skip 0.1.4.
5. Wait until **HUD is fully up**, THEN enable the execute breaks (avoids init spam).
6. Save state before last kill.
7. Kill last enemy.

## On first stop after the kill

Screenshot full debugger and note:

```
post-kill execute 800A1500:
  pc: ........
  ra: ........
  hit count: ..
  game moment: (black frame / poses / rewards?)
  s5 / any 800F83xx in regs: ........
```

Press continue a few times if it re-enters; screenshot if **pc or ra changes** to a new region.

If **800A1500 never hits** after kill (only earlier), say so and try execute **800A1540** only.

## Why this matters

We still need the **pose** controller. This flag function mutates win-state (incl. bit 0x20). Tracing it post-kill should show the call path into poses / rewards without drowning in the GTE loop.

## Do not

- Do not re-enable **800D3098**
- Do not use execute **800A54A0** (old wrong guess on shared overlay)

## When done

Push screenshots under docs/ or paste the block in chat.

first break after kill, game moment right after the enemey kill animation ends and before and fanfair animations start
after the 7th I just hit unpause 3 more times for a total of 10 and immediatly after the breaks stopped the fanfair animation starts with no more breaks all the way into the rewards and beyond