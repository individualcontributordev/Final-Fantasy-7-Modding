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

### Live PCs from human shots (2026-08-09)

| Shot | File | pc | Use |
|------|------|-----|-----|
| Win pose **start** (human) | `docs/victory-pose-start-debugger.png` | **`0x800D3098`** | Primary next execute BP |
| Mid win anim | `docs/victory-pose-mid-anim-debugger.png` | `0x800C63AC` | Render/color path — skip for control flow |

**Start-shot registers (important):**

- `s4 = 0x800F83C6` — Exit Battle Status (matches RAM map)
- `s1 = 0x800F83E0`, `s5 ≈ 0x800F836C` — battle-end block
- `gp = 0x80062D44` — near battle globals
- `ra = 0x8003CF98` — callee return into low/system region
- Code at `pc` loads **`0x80051568`** (global frame counter) then branches

**Note:** Those instruction bytes are **not** at `BATTLE.X_file + 0x800A0000` in our extract (same address space as battle overlay data, but base/mapping still open). Static file offsets for pose/music patches remain valid; live **0x800D3098** was tested and is a per-frame renderer (see below), not the pose hook.

### Next breakpoints (see INSTRUCTIONS)

1. **Off:** execute `0x800D3098`; write `F83C6` done (mapped)
2. **On after HUD:** execute `0x800A1500` / `0x800A1540` / `0x800A1580`
3. Map caller `ra=800A1408` and pose branch


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

1. Write F83C6 mapped to BATTLE.X 0x154C/0x1584 (done).
2. Execute 800A1500 region after HUD; trace pose branch.
3. D3098 stays off.


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
