#!/usr/bin/env python3
"""Update fanfare findings + INSTRUCTIONS after 800D3098 every-frame pass."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FIND = REPO / "docs/findings/2026-08-09-fanfare-skip-duckstation-compare.md"
INST = REPO / "docs/INSTRUCTIONS.md"
IDX = REPO / "docs/findings/README.md"

SECTION = """
## Live pass: 800D3098 every-frame (disproven as pose hook)

**Human (550d529):** 800D3098 hits **every battle frame**. Write activity on 800F83C6 goes quiet once EXP/rewards is open.

### Screenshots

| File | Moment | pc | D3098 hit count (status) | Notes |
|------|--------|-----|--------------------------|-------|
| docs/before last.png | Before last kill | 800D3098 | 53 | Same GTE loop |
| docs/after last, before animations.png | After kill, before win anim | 800D3098 | 54 | +1 only → still per-frame |
| docs/mid animations.png | Mid win anims | 800D3098 | 76 | Still same PC |
| docs/read value.png | Battle-end RAM view | pc 800D3098 | — | **F83C6 = 0x00** at that pause |

### What 800D3098 actually is

Disassembly is a **GTE / mesh transform loop** (mfc2/swc2/lwc2, vector loads, bne t8).  
ra stays **8008A9CC** (renderer caller).

**Not** victory control. Earlier "pose start" pause landed on the busy renderer by chance. **Disable execute BP 800D3098.**

### 800F83C6 (exit status)

- Early win window (read value.png): byte **0** (not Victory=1 yet).
- Human: break goes idle after rewards UI → writes are in the **kill → rewards** handoff; need **first write** pc.

### Next hook strategy

1. No execute on 800D3098 / 800A pose guesses.
2. **Write** break on 800F83C6 (1 byte) armed **before last kill**; screenshot **first** hit (pc, ra, value).
3. Backup: write on last enemy HP to 0 for kill timing only.
4. If first F83C6 write is already rewards-only, manual pause at first pose frame with D3098 off.
"""


def main() -> None:
    t = FIND.read_text(encoding="utf-8")
    t = t.replace(
        "live hook uses **`0x800D3098`**.",
        "live **0x800D3098** was tested and is a per-frame renderer (see below), not the pose hook.",
    )
    t = t.replace(
        """### Next breakpoints (see INSTRUCTIONS)

1. Execute **`0x800D3098`** once per win (confirm hit count / ra / stack)
2. Optional write on **`0x800F83C6`**
3. Keep `800A…` pose guesses **off**
""",
        """### Next breakpoints (see INSTRUCTIONS)

1. **Off:** execute `0x800D3098` (every-frame GTE)
2. **On:** write `0x800F83C6` — capture **first** hit after last kill
3. Keep `800A…` pose guesses **off**
""",
    )
    if "800D3098 every-frame" not in t:
        # insert before Patch direction
        needle = "## Patch direction (after hits)"
        if needle in t:
            t = t.replace(needle, SECTION + "\n" + needle)
        else:
            t = t.rstrip() + "\n" + SECTION
    FIND.write_text(t, encoding="utf-8")

    fence = chr(96) * 3
    INST.write_text(
        f"""# Task: Catch the first write to exit-battle status

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

{fence}
first F83C6 write:
  pc: ........
  ra: ........
  value at 800F83C6: ..
  hit count: 1 (or ?)
  game moment: (poses? rewards? still fighting?)
{fence}

6. If it never breaks between kill and rewards, say so.
7. If the first break is only on the rewards screen, also **manual pause** at the first win-pose frame (D3098 off) and screenshot pc.

## Do not

- Do not leave **800D3098** execute on
- Do not use old **800A54A0**-style execute breaks

## When done

Push screenshots under docs/ or paste the pc/ra/value block in chat.
""",
        encoding="utf-8",
    )

    idx = IDX.read_text(encoding="utf-8")
    for line in idx.splitlines():
        if "fanfare-skip-duckstation-compare" in line:
            new = (
                "| 2026-08-09 | [fanfare-skip-duckstation-compare](2026-08-09-fanfare-skip-duckstation-compare.md) "
                "| 800D3098 is per-frame GTE loop (not pose); next F83C6 write | in-progress |"
            )
            idx = idx.replace(line, new)
            break
    IDX.write_text(idx, encoding="utf-8")
    print("updated findings, INSTRUCTIONS, index")


if __name__ == "__main__":
    main()
