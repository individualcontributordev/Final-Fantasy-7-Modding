#!/usr/bin/env python3
"""Record F83C6 write hits (800A15xx) and refresh INSTRUCTIONS."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FIND = REPO / "docs/findings/2026-08-09-fanfare-skip-duckstation-compare.md"
INST = REPO / "docs/INSTRUCTIONS.md"
IDX = REPO / "docs/findings/README.md"

SECTION = """
## Live pass: F83C6 write hits (FOUND)

**Human (0446946 + chat):** Write BP on `800F83C6` fires a few times at fight **start** (before/during HUD load), then **stops mid-battle**, then **4 hits after final kill**, then silent through world map.

### Post-kill screenshots (Hit Count 40–43)

| File | pc (after write) | Path | Notes |
|------|------------------|------|-------|
| after final kill first break.png | **800A1550** | clear bits then continue | s5=F83C6; after `sh a0,0(s5)` @154C |
| after final kill second break.png | **800A1588** | OR **0x20** store | after `sh v0,0(s5)` @1584 |
| third break.png | **800A1550** | clear path again | F83C6 halfword shows **0x0061** |
| fourth break.png | **800A1588** | OR 0x20 again | still 0x61; no further hits |

Shared on all four:
- **s5 = 0x800F83C6** (base for the halfword store)
- **ra = 0x800A1408** (caller in same overlay)
- Status line: `Hit Write breakpoint … at 0x800F83C6`
- Disasm matches **BATTLE.X_dec file** at `0x1500+` 1:1 (confirmed on disk)

### BATTLE.X sites (live = 0x800A0000 + file)

```
file 0x1540  lhu v0, 0(s5)         ; load flags at F83C6
file 0x1548  andi a0, v0, 0xFFDD   ; clear bits 0x0022
file 0x154C  sh a0, 0(s5)          ; WRITE A
file 0x1578  ori v0, a0, 0x0022    ; optional set 0x22
file 0x1580  ori v0, a0, 0x0020    ; set bit 0x20 (no-music / special end)
file 0x1584  sh v0, 0(s5)          ; WRITE B
```

**0xFFDD** clears **0x22** (bits 1 + 5). Later path can OR **0x20** or **0x22** back.
Community "byte exit status" is at least a **halfword flag** here; value **0x61** after settle.

### Why early-fight hits

Same function **initializes** F83C6 during battle setup (pre-HUD). After HUD, quiet until win transition. Not a mid-battle spam address.

### Patch relevance

- This is a **real BATTLE.X control path**, not the D3098 renderer.
- Bit **0x20** on this halfword is the same class of "special end" flag the old global force tried (and still left poses). Editing only 0x20 here may quiet music path but **poses need a different gate** (likely queue @ file `0x2974` already ret'd, or pose sites `0x5484`/`0x54A0`, or caller of this block).
- Next: **execute** into this function after last kill and find **who jumps to win poses**.

### Next breakpoints

1. Keep write `F83C6` off (or leave as noise check).
2. Arm execute **after HUD is up**, before last kill:
   - **800A1500** (block entry / loop head) — prefer first
   - **800A1540** (load flags before mutate)
   - **800A1580** (ORI 0x20 path)
3. On first post-kill stop: screenshot full CPUDebugger + note game moment (poses started?).
4. Optional: run once with Fanfare Skip **off** (stock) and once **on** — same pcs?

"""


def main() -> None:
    t = FIND.read_text(encoding="utf-8")
    t = t.replace(
        """### Next breakpoints (see INSTRUCTIONS)

1. **Off:** execute `0x800D3098` (every-frame GTE)
2. **On:** write `0x800F83C6` — capture **first** hit after last kill
3. Keep `800A…` pose guesses **off**
""",
        """### Next breakpoints (see INSTRUCTIONS)

1. **Off:** execute `0x800D3098`; write `F83C6` done (mapped)
2. **On after HUD:** execute `0x800A1500` / `0x800A1540` / `0x800A1580`
3. Map caller `ra=800A1408` and pose branch
""",
    )
    if "F83C6 write hits (FOUND)" not in t:
        needle = "## Patch direction (after hits)"
        if needle in t:
            t = t.replace(needle, SECTION + "\n" + needle)
        else:
            t = t.rstrip() + "\n" + SECTION
    # soften old "800A pose guesses off" in strategy if still conflicting
    t = t.replace(
        "1. No execute on 800D3098 / 800A pose guesses.\n"
        "2. **Write** break on 800F83C6 (1 byte) armed **before last kill**; "
        "screenshot **first** hit (pc, ra, value).\n"
        "3. Backup: write on last enemy HP to 0 for kill timing only.\n"
        "4. If first F83C6 write is already rewards-only, manual pause at first pose frame with D3098 off.\n",
        "1. Write F83C6 mapped to BATTLE.X 0x154C/0x1584 (done).\n"
        "2. Execute 800A1500 region after HUD; trace pose branch.\n"
        "3. D3098 stays off.\n",
    )
    FIND.write_text(t, encoding="utf-8")

    fence = chr(96) * 3
    INST.write_text(
        f"""# Task: Trace the F83C6 flag function (win transition)

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

{fence}
post-kill execute 800A1500:
  pc: ........
  ra: ........
  hit count: ..
  game moment: (black frame / poses / rewards?)
  s5 / any 800F83xx in regs: ........
{fence}

Press continue a few times if it re-enters; screenshot if **pc or ra changes** to a new region.

If **800A1500 never hits** after kill (only earlier), say so and try execute **800A1540** only.

## Why this matters

We still need the **pose** controller. This flag function mutates win-state (incl. bit 0x20). Tracing it post-kill should show the call path into poses / rewards without drowning in the GTE loop.

## Do not

- Do not re-enable **800D3098**
- Do not use execute **800A54A0** (old wrong guess on shared overlay)

## When done

Push screenshots under docs/ or paste the block in chat.
""",
        encoding="utf-8",
    )

    idx = IDX.read_text(encoding="utf-8")
    for line in idx.splitlines():
        if "fanfare-skip-duckstation-compare" in line:
            new = (
                "| 2026-08-09 | [fanfare-skip-duckstation-compare]"
                "(2026-08-09-fanfare-skip-duckstation-compare.md) "
                "| F83C6 writes = BATTLE.X 0x154C/1584; next exec 800A1500 | in-progress |"
            )
            idx = idx.replace(line, new)
            break
    IDX.write_text(idx, encoding="utf-8")
    print("ok")


if __name__ == "__main__":
    main()
