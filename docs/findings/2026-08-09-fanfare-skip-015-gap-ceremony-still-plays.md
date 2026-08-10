# Finding: Fanfare Skip 0.1.5 still plays fanfare + poses

**Date:** 2026-08-09
**Status:** fixed in fanfare-skip-v0.1.6 (BATRES skip-setup)
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

## First-hit audio / 33E34 pass (deafeab)

### Observed hit order (operator)

1. **80033E34** — *before victory* (enemies still up; blue action menu). HitCount 5
   already. `a0=0x801C1A` (not the 14540 globals path). **General frame pump — spam.**
2. **801B0278** — victory path after kill (`jal 801B0E20`). 03D0 still 0. 14540 still 0.
3. **80033E34** again
4. **80014540** — **mid fanfare**, win poses on (`docs/80014540 fourth.png`)
   - a0=`0x801C410`, a1=`0x8005C2C6`, a2=`0xDECC` (loaded from globals inside wrapper)
   - **801B03D0 HitCount stayed 0** whole fight
5. **80033E34** mid fanfare; later on world-map load

### Corrections

1. **`80033E34` is not victory-specific.** Drop as fanfare start probe.
2. **Normal ceremony path often skips 801B03D0.** Static BATRES:

```
03A0: s4 = 0x31; *8010A6B8 = 1
03C4: s0 = *A6B8 | *80163B80
03C8: if s0 != 0 → skip 03D0
03E0: for i in s4: jal 800A3354   # ceremony wait
042C: if s0 != 0 → jal 80014540   # this is the 14540 that hit
```

First `80014540` = **801B042C** after wait, not 03D0. Prior "03D0 looping" was
likely wait/re-entry confusion; this pass proves **03D0=0** while ceremony plays.

3. Fanfare+poses already on at first **80014540** ⇒ start is **between 801B0278 and
   end of s4 wait**, not inside 14540/33E34.

### Bracket for start of music/poses

| After | Before |
|-------|--------|
| 801B0278 (`jal 801B0E20`) | first mid-fanfare frame |

Candidates inside BATRES after 0278:

| VA | Call |
|----|------|
| 801B028C | `jal 800A7254` a2=4 (×10) — pose/anim seed |
| 801B02FC | `jal 800B1060` a0=8 (conditional) |
| 801B03A0 | `s4=0x31` + set ceremony flag |
| 801B03E0 | wait loop `800A3354` × s4 |
| 801B042C | `jal 80014540` (post-wait; mid fanfare) |

## Ghidra decompile pass (28c2c5c)

Clean archive: docs/ghidra-pastes/batres-victory-path.md

### Callee roles (from decompile)

| VA | Ghidra | Role |
|----|--------|------|
| 800A7254 | FUN_800a7254(slot, type, subtype, extra) | Queues one actor anim/action if slot free. Not music. |
| 800A3354 | FUN_800a3354 | Battle frame tick (pump, actor sync). Wait engine; not song start. |
| 800B1060 | FUN_800b1060(p) | Thin to FUN_800a31a0(10,2,1,p). Side path only. |
| 800A56B0 | FUN_800a56b0(id) | Drain/process queued UI ids (rewards). |
| 80014540 | FUN_80014540 | SCUS wrapper to 80033e34(globals,0). |
| 80033E34 | FUN_80033e34 | to FUN_80033cb8(cmd=3, ...). Global pump. |
| 801B0E20 | batres_clear_battle_ui | Clear UI slots; not music. |

### batres_victory ceremony core (annotated)

After flag munging and batres_clear_battle_ui():

1. for i in 0..9: FUN_800a7254(0, i, 4, 0) — queue anim type 4 on 10 slots (win pose/anim seed).
2. Mask some battle state words with 0x1831.
3. Branch on battle end flags (uVar4 bits):
   - bit8 set: skip special wait setup
   - else bit2: iVar17=0x1E; 800b1060(8); flag 80163b80=1
   - else bit4: iVar17=8; write actor bytes 0xE
   - else special: write actor bytes 0xC; iVar17 = 0x31; DAT_800fa6b8 = 1  (normal win path)
4. if both ceremony flags 0: FUN_80014540() once (pre-wait pump)
5. for i in 0..iVar17: FUN_800a3354() — blocking ceremony wait (0x31 ~ 49 frames)
6. while flags still set: FUN_800a3354()
7. if flags were set at entry to wait: FUN_80014540() again
8. then rewards loops (800a56b0), 800dcf94(-1) clear, exp/items UI

### Patch targets (next experiment)

Ceremony length / visible win staging is dominated by:

- Anim seed: 800a7254(..., 4, 0) x10 — removing may kill poses (test).
- Wait count iVar17=0x31 (RAM: ori s4, zero, 0x31 @ 801B03A0) — set to 0 or 1 to shorten.
- DAT_800fa6b8 = 1 — drives skip of first 14540 and the while-flag spin.

Music is NOT started inside 800a7254 / 800a3354 / 80014540. Fanfare is either
already requested before/at batres entry from BATTLE.X (0.1.5 stubs 800A2974 only),
or triggered by anim type 4 side effects / parallel sound path still live in BATTLE.

First binary experiment (BATRES only): force iVar17/s4 = 0 (patch ori s4, zero, 0x31
to ori s4, zero, 0) so ceremony wait is skipped; smoke whether fanfare still plays
and whether flow reaches rewards cleanly.

Do NOT quiet FAN2.SND (known freeze).

## BATRES s4=0 smoke (48e83ca build)

Image: pristine D1 + BATRES wait counts forced to 0 only (anim seed kept).

Operator result:

- Fanfare music + win animations **still start** at kill (same as stock timing).
- Screen **immediately** fades black into **rewards** (ceremony hold gone).
- Fanfare **keeps playing in full on the rewards page**; rewards BGM only after fanfare ends.
- (Implied: no freeze; rewards reachable.)

### Conclusion

s4 wait loop only **holds** the victory camera/field before loot. It does **not**
gate starting fanfare or win poses. Shortening wait is a UX partial win (faster loot)
but **not** a fanfare/pose kill.

Fanfare duration is independent of that wait (plays over rewards until song ends).

### Next smoke

Also **nop** jal 800A7254 at 801B028C (anim type-4 seed) while keeping s4=0:

- If poses die and/or fanfare dies -> seed is the start path (or both).
- If fanfare still plays without poses -> music starts elsewhere (before/parallel BATTLE).
- If both still play -> start is earlier than this BATRES block.

## BATRES s4=0 + nop anim4 smoke

Operator: **animations still there** (with wait=0 and jal 800A7254 nopped).

### Conclusion

Win poses (and likely fanfare start) do **not** depend on the BATRES type-4
800A7254 seed loop alone. Other candidates still in BATRES setup (02E0-03B0):

- sb actor bytes 0xC / 0xE
- DAT_800fa6b8 / DAT_80163b80 ceremony flags
- or start entirely before/outside this block (BATTLE.X on kill)

Next: force-skip entire setup via j 801B03B0 at 801B02E0.

## BATRES skip-setup smoke — SUCCESS

Operator: force j 801B03B0 at 801B02E0 (+ s4=0 + nop 7254):

- **No animations**
- **No fanfare music**
- Battle ends after final kill (continues into end/rewards flow)

### Root cause (ceremony start)

The BATRES block 801B02E0-801B03B0 (actor mode bytes 0xC/0xE, ceremony
flags, wait setup) is required to **start** fanfare + win poses. Skipping it
matches the intended mod.

s4 wait and 800A7254 type-4 seed alone were insufficient.

### Ship

Packaged as **fanfare-skip-v0.1.6** (BATRES GZIPPS patch only; all 3 discs;
clean/CSR/Highwind packs). Replaces 0.1.5 in manifest (0.1.5 disabled).

