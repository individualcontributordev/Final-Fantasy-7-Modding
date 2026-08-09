# Notes from import (agent + human)

## Source

Imported from community **FF7 Memory Values** workbook (PSX Address List).
Not Square-official. Tags are ours for search.

## DuckStation

Workbook CE sheet: DuckStation is roughly RAM-pointer + offset.
For main RAM watches we use **`0x80000000 + offset`** (matches fanfare RE).

## Important correction for Fanfare Skip

| Offset | Workbook name | Implication |
|--------|---------------|-------------|
| `62D78` | Battle Controller Inputs | **Not** battle-mode flags |
| `62D7A` | Battle Controller Inputs Copy | Same family |
| `62D88` / `62D8A` | Battle-frame input copies | 15fps; frozen while paused |

DuckStation screenshots paused at `0x8001CC20` (loads `0x2D78`/`0x2D7A`, store `0x2D7C`) match **input copy/XOR logic**, not BTLMD mode bits.

A write-break only on `80062D7C` is a poor fanfare/pose hook. Prefer execute breaks in `BATTLE.X` (`0x800A…`) or named battle-end RAM below.

## Battle-end related (from list)

Tag `battle-end` or description **Exit Battle Status**:

- `F83C6` (`0x800F83C6`) — Exit battle status (+ party lock bits).  
  Notes: `1=Victory`, `3=Game Over`, `4-5=Run Away`, `8-F=Fade Out Exit`; high bits disable party/menu.

Also `F83AE` (weird battle outcome / AI stall tests in notes).

## Not imported as primary DB

- **PC Addresses** / **PC Address List** — different process; add later if needed.
- **Cheat Engine base formulas** — emulator-specific (workbook sheet 4).
