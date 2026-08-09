# Fanfare Skip — DuckStation compare (normal vs train)

**Date:** 2026-08-09
**Status:** screenshots reviewed (`ef0d4d0`); need execute BPs on battle code
**Mod:** Fanfare Skip v0.1.4 (`0110cf4`)

## Playtest (v0.1.4)

| Item | Result |
|------|--------|
| Auto-confirm | Fixed |
| Victory music | Off |
| Win poses | Still on normal |
| Stuck audio until rewards | Still sometimes |

## Screenshots in `docs/` (human, `ef0d4d0`)

| File | Moment |
|------|--------|
| `normal before fanfair.png` | Normal fight, mid-battle (party ATB up) |
| `normal fanfair start.png` | Normal, paused around fanfare/pose start |
| `normal after fanfair rewards.png` | Normal, after rewards |
| `trains before fanfair.png` | Train fight before win show |
| `trains after fanfair.png` | Train after win |

## What the shots show

1. **Write BP on `0x80062D7C` never fired** (Hit Count **0** on every shot).
2. **Memory at `0x80062D7C` is `00 00`** on normal *and* train (before/start/after).
   These pauses do **not** show a train-only skip value at that halfword.
3. **PC is not in the battle overlay.** Examples:
   - mid-battle: `pc = 0x800D3074`
   - fanfare start / rewards / train: `pc ≈ 0x8001CC20`
   That is main/kernel-style code (loads around `0x2D78` / store `0x2D7C`), **not** `BATTLE.X` at `0x800Axxxx`.
4. Code at `0x8001CC1C` **computes** a store to `0x2D7C` from halfwords at `0x2D78`/`0x2D7A` — not a plain field flag dump. Hit Count 0 means that write did not run while the BP was armed (or freezes are not during a write).

**Conclusion (updated):** Execute breaks at file+`0x800A0000` for pose sites are **wrong in practice**.

Human report: those `800A…` execute breaks **do not hit during battle**; they **spam on the world map** (must pause every frame) and only catch after rewards when the world/field overlay is loading again.

### Why

FIELD, WORLD, and BATTLE **share the same overlay load slot** (~`0x800A0000`). Addresses like `0x800A54A0` are **field/world code** while idling on the map, not a stable “BATTLE pose PC.” Mid-battle PC from earlier shots (`0x800D3074`) is consistent with battle code running **elsewhere in that large overlay**, not at our guessed file offsets under a frozen `800A` label.

### File offsets still matter for patching

Static patches stay on **BATTLE.X file offsets** (`0x2974`, `0x54A0`, …). Live DuckStation PCs must be **read from a pause at pose start**, then mapped back — do not assume `PC = 0x800A0000 + file_off` for breakpoints until a hit confirms it.

### Next breakpoints (see INSTRUCTIONS)

1. **Pause at pose start** → record `pc` / `ra`
2. **Write** break on exit status `0x800F83C6` (byte; notes say `1 = Victory`)
3. Clear all old `800A54A0` / `800A5484` / `800A2974` / `800ABE4C` execute breaks

## Patch direction (after hits)

- Skip/NOP pose path at `0x54A0` / gate at `0x5484` **without** global mode-bit force.
- Stop requesting song id `0x2F` (stuck audio) rather than only silencing `FAN2.SND`.

## Memory map cross-ref (2026-08-09 import)

Community list in `docs/reference/ff7-psx-memory/`:

- `62D78` / `62D7A` = **battle controller inputs**, not BTLMD mode bits
- Battle-end status candidate: `F83C6` (`0x800F83C6`) — Exit Battle Status (`1=Victory`, …)

Query: `python3 docs/reference/ff7-psx-memory/query_memory.py --tag battle-end`

## Human task

See `docs/INSTRUCTIONS.md` — execute BPs on the addresses above during a normal win.
