# Notes from import

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

A write-break only on `80062D7C` is a poor fanfare/pose hook.

**Do not** put long-lived execute breaks on guessed `0x800A…` battle file offsets — FIELD/WORLD/BATTLE share that overlay slot, so those PCs spam on the world map and miss the win pose. Prefer: pause at pose start and read `pc`, and/or write-break battle-end RAM below.

## Battle-end related (from list)

Tag `battle-end` or description **Exit Battle Status**:

- `F83C6` (`0x800F83C6`) — Exit battle status (+ party lock bits).  
  Notes: `1=Victory`, `3=Game Over`, `4-5=Run Away`, `8-F=Fade Out Exit`; high bits disable party/menu.

Also `F83AE` (weird battle outcome / AI stall tests in notes).

## Enemy current HP (playtest 2026-08-09)

Live actor HP uses the **same 0x68 stride** as player battle slots:

| Slot | Current HP (2 bytes) |
|------|----------------------|
| Enemy 1 | `F85AC` → `0x800F85AC` (confirmed) |
| Enemy 2 | `F8614` → `0x800F8614` (confirmed) |
| Enemy 3 | `F867C` → `0x800F867C` (confirmed) |
| Enemy N | `F85AC + (N-1)*0x68` |

Formula: **`0x800F85AC + (N-1)*0x68`**.

Spreadsheet rows at `F875C` / `F87C4` etc. are a **stats-block copy** — they do **not** track on-screen HP. DB labels those `(stats block)`.

## Not imported as primary DB

- **PC Addresses** / **PC Address List** — different process; add later if needed.
- **Cheat Engine base formulas** — emulator-specific (workbook sheet 4).
