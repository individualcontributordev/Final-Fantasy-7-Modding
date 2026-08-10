# Finding: Fanfare Skip 0.1.5 still plays fanfare + poses

**Date:** 2026-08-09
**Status:** confirmed (smoke) / fix open
**Module:** BATTLE.X + BATRES victory phase

## Smoke (0.1.5 clean D1)

| Symptom | Result |
|---------|--------|
| Held tone freeze | **no** (quiet FAN2 removed) |
| Fanfare music | **yes** still heard |
| Win poses | **yes** still shown |
| Loot / exp | OK |

## What 0.1.5 actually does

Only patches victory-queue at file+**0x2974** (`800A2974`) to immediate `jr ra`.
Single static caller: **`jal 800A2974` @ 800ABE4C**.

Stock FAN2.SND left alone (required — zero-body FAN2 freezes SPU).

## Implication

Ceremony audio + poses are **not exclusively** driven by `800A2974`. Need live
post-kill hits for:

1. Whether **800ABE4C** still runs (stub reached vs bypassed)
2. First **music engine** entry (`80015248` AKAO helper and/or `800DCF94` with a0≠-1)
3. Timing vs known BATRES path (`801B0000` → … → `801B0558` clear)

Abandoned approaches (do not revive without new evidence):

- Quiet FAN2.SND body → freeze
- Global force battle-mode bit 0x20 / 0x100 → auto-confirm / wrong end UI

## Next

DuckStation BP pass on official 0.1.5 image (see `docs/INSTRUCTIONS.md`).

## Live BP pass (4ff7341, 0.1.5 image)

Human order after last kill:

1. **80015248** — many hits while death anim still running (general SFX; noisy)
2. **801B0000** — BATRES entry; **no fanfare, no win anim yet**
3. **800DCF94** — then more 15248 / DCF94 alternating
4. Later cluster of **800DCF94** then **fanfare anims start**
5. **80015248** continues after battle ends

### Screenshots / regs

| Shot | PC | Notable regs | BP hit counts (panel) |
|------|-----|--------------|------------------------|
| docs/80015248.png | 80015248 | a0=5 a1=1 a2=0 ra=**8002ECC** | 15248 high; DCF94≈9; **ABE4C=1**; 801B=1 |
| docs/801B0000.png | 801B0000 | ra=**800A1734** s5=800F83C6 | ABE4C already 1 |
| docs/800DCF94.png | 800DCF94 | **a0=a1=a2=-1** ra=800C55E8 | clear path |
| docs/800DCF94 right before fanfair I think.png | 800DCF94 | **a0=-1** ra=800C5F68 s2=0x20 s4=0x31 | clear; user: near fanfare |

### Conclusions

| Probe | Result |
|-------|--------|
| **800ABE4C** | **HIT once** — victory-queue stub is reached this fight |
| **800DCF94** | Hits seen are **a0==-1 clears only** (not song set) |
| **80015248** | Too noisy; first post-kill hits are not fanfare-unique |
| Fanfare audible / anims | After BATRES; clustered with later DCF94 clears, not a smoking set-id shot |

### Static candidates for real FAN2 start (next BPs)

FAN2 AKAO id **0x47** appears at:

- `800AB2B0` delay: `ori a0, zero, 0x47` then `jal 800A2CC4` @800AB2AC
- nearby `jal 800B1060` @**800AB2D0** (same block)

Do **not** keep 80015248 armed for fanfare isolation.

## FAN2 0x47 BP pass (145a809) — NEGATIVE

| BP | In-battle (during win ceremony)? | After rewards / world map? |
|----|----------------------------------|----------------------------|
| **801B0000** | **YES** (only hit in battle) | — |
| **800AB2AC** | **NO** | YES (then loops with AB2D0) |
| **800AB2D0** | **NO** | YES |
| **800A2CC4** | **NO** | YES |
| **800B1060** | **NO** | YES |

User: *only 801B0000 hit in battle; all others after rewards; AB2D0/AB2AC loop loading world map.*

### Overlay trap

Post-rewards code at `800AB2AC` in the shot is **not** BATTLE.X (`jal 800A2CC4` /
`ori a0,0x47`). Live disasm differs — **world map (or other) overlay reused the VA**.
Those hit counts must **not** be treated as victory-fanfare calls.

### Conclusion

Victory **fanfare + poses on 0.1.5 happen without** the FAN2-id `0x47` block at
`800AB2AC`. Ceremony audio starts on the **BATRES path after 801B0000**, still
in battle, before rewards. Next probes = BATRES-internal jals while still on
victory screen (not AB2*).

## BATRES-path BP pass (3eff3a6)

### In-battle order (screenshot names)

1. **801B0000** — first hit (`docs/801B0000 first hit.png`)  
   - ra still win_transition path; battle field visible; no ceremony yet  
   - Hit counts at this moment: 0278/03D0/010C/0458/03E0/0524/06D8 all **0**
2. **801B0278** — second (`docs/801B0278 second.png`) — `jal 801B0E20`  
   - 03D0 still 0
3. **801B03D0** — third (`docs/801B03D0 third.png`) — `jal 80014540`  
   - User: **loops during fanfare music and animations**
4. **801B0524** (`docs/801B0524.png`) — `jal 800A56B0`  
   - User: **loops after, as rewards page loading** (black fade shot)

### Hit / miss (in-battle)

| BP | In battle? | Notes |
|----|------------|-------|
| 801B0000 | YES | anchor; can re-enter (hit count 2 already on first shot footer) |
| 801B010C | **NO** (0) | not on this path |
| 801B0278 | YES | after entry |
| 801B03D0 | YES | **ceremony loop** ↔ fanfare + win anims |
| 801B03E0 | 0 in panels | may still run after 03D0 return (not left running) |
| 801B0458 | 0 | not observed |
| 801B0524 | YES late | **rewards**, not fanfare start |
| 801B06D8 | 0 | not observed |

### Static: what 801B03D0 is

`jal 80014540` (SCUS) → thin wrapper → `jal 80033E34` with globals  
`a0=*(80071744)`, `a1=*(80095DD8)`, `a2=*(800722C8)`, `a3=0`.  
`80033E34` → `jal 80033CB8` with **a0=3** (command class).

BATRES around it: if `s0==0` call 14540; then if `s4!=0` loop `jal 800A3354` up to s4 (often 0x31); spin; optional second 14540 @042C.  
**801B0000 re-entry** each frame explains **03D0 looping** while music/anims play.

### Bracket

| Phase | Marker |
|-------|--------|
| Before ceremony audio/anims | ≤ 801B0278 |
| During fanfare + win poses | **801B03D0 / 80014540 loop** |
| Rewards UI | **801B0524** |

Patch target class: shorten/skip BATRES ceremony wait (03D0–0430 region / s4 loop / 14540 pump) **without** quiet FAN2. Confirm music is already requested before first 03D0 vs only sustained by the loop.
