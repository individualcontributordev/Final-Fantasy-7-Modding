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

**Conclusion:** Next useful breakpoint is **execute** on battle poses/music, not only a write on `0x2D7C`.

## BATTLE.X runtime addresses (base `0x800A0000`)

| Role | File off | Break (execute) |
|------|----------|-----------------|
| Victory queue (v0.1.4 stub) | `0x2974` | `0x800A2974` |
| Only `jal` to that queue | `0xBE4C` | `0x800ABE4C` |
| Pose gate (bit `0x20`) | `0x5484` | `0x800A5484` |
| Write win anim index `7` | `0x54A0` | `0x800A54A0` |
| Anim setup function | `0x5250` | `0x800A5250` |
| Fanfare song id `0x2F` | `0x1CE0`, `0x2ADC`, `0x8658` | same + base |

If `0x800A2974` never hits on a normal win, live load base may differ — search RAM for stub bytes.

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
