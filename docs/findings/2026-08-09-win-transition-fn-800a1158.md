# Win-transition function 800A1158 (BATTLE.X)

**Date:** 2026-08-09  
**Confidence:** confirmed (live DuckStation + static disasm)  
**Status:** open  
**Related:** `docs/INSTRUCTIONS.md`, fanfare-skip findings 2026-08-08/09

## Summary

Post-kill breakpoints at **800A1500 / 800A1540 / 800A1580** all sit inside one large BATTLE.X function **`fun_800A1158`** (file+0x1158 … jr ra at **800A1790**). It owns halfword **800F83C6** (`s5`), drives a multi-frame wait loop, then exits into overlay load / **jal 801B0000** — and that is exactly when fanfare/win poses begin.

## Context

Write-BP on 800F83C6 gave 4 post-kill stores from 800A15xx. Goal: find pose controller without 800D3098 spam. User enabled execute BPs at 1500/1540/1580 after HUD-up, killed last enemy; 7+ continues, then **~10 total hits and breaks stop as fanfare starts**.

## Discovery

### Identity

| Item | Value |
|------|--------|
| Entry | **800A1158** (`addiu sp,sp,-56`) |
| Exit | **800A1790** `jr ra` |
| File | `BATTLE_X_dec.bin` +0x1158 … +0x1794 |
| Flag ptr | `s5 = 800F83C6` set at **800A11F0–11F4** |
| Companion | `s7 = 8016376A` (battle-mode-ish halfword) |

No static `jal 800A1158` inside BATTLE.X (pointer/jalr entry — outer caller still unknown).

### Live shots (post-kill, Fanfare Skip 0.1.4)

Common on stops inside the 1500 triad:

- `s5 = 800F83C6`, `ra = 800A1408` (delay slot of **inner** copy loop, not outer caller)
- Hit counts climb (1500 ≈ 31→35; 1540/1580 ≈ 10→11)
- Game moment: after death anim, **before** fanfare/poses
- After ~10 continues total: **no more hits**; fanfare begins; rewards later

So this function is the **pre-fanfare gate**, called/iterated until a wait condition clears, then it falls through and fanfare code runs.

### Flag ops on 800F83C6 (confirmed disasm)

```
800A1540  lhu  v0, 0(s5)
800A1548  andi a0, v0, 0xFFDD     # clear bits 0x22
800A154C  sh   a0, 0(s5)
… mask vs 800F7DCE / 8016375A …
800A1578  ori  v0, a0, 0x22       # or
800A1580  ori  v0, a0, 0x20       # set bit 0x20
800A1584  sh   v0, 0(s5)
```

Optional later: `ori … 0x30` when `(*s7 & 2)` and a 800A-relative word is 0.

### Structure (high level)

1. **Prologue / setup** 1158–12F0 — copy bytes, strip bit on 801083D0, jalr into 800B/801B helpers  
2. **Main body** loops (fp counter); includes **800A13A0 `sh zero,0(s5)`** (clears flag once per pass path)  
3. **Actor/HP sync** 14F0–153C — 3× compare 800F5E6C vs 80108408; on mismatch `jal 800A7254(a0=0,a1=slot,a2=0xC,a3=0xF)` (**anim/cmd queue**)  
4. **Flag mutate** 1540–15DC (above)  
5. **Wait / exit** 16B0–1790:
   - if `(halfword 801083C6 & 0x1E) == 0`:
     - load status from 80163616; maybe `jal 800A35F8`
     - **`bne s1,0xFFFF → 800A1200`** (loop again; **this is the multi-frame wait**)
   - else fall through: `jal 80014578/145BC/15CA0`, **`jal 801B0000`**, restore 4 bytes, `sh 1 → 800AC560`, return

While 1500/1540/1580 keep hitting, the wait branch is still looping. When they stop, the function took the fall-through and **801B0000** (victory-phase overlay) ran — fanfare/poses live there or immediately under it.

### Important callees

| Addr | Role (inferred) |
|------|------------------|
| **800A7254** | Queue battle cmd/anim (`a2` = type; win path uses **0xC**) |
| **800A72C8** | Related queue with `a0=2` |
| **800A4540 / 4480** | Party/state copy helpers |
| **800A56B0** | Table tick with `a0=0xA` |
| **800A35F8** | Wait-status helper on loop |
| **801B0000** | Loaded overlay entry after wait ends |

### Not the old wrong targets

- **800A54A0** — different function; do not BP  
- **800D3098** — renderer; do not BP  

## How we found it

DuckStation execute BPs at 800A1500/1540/1580 after final kill (user shots first–7.png + notes). Static disasm of `workspace/iso-extract/BATTLE_X_dec.bin` mapped prologue 1158 ↔ epilogue 1790 and the 16F4 back-edge to 1200.

## Why it matters

- Fanfare Skip music bits alone do not skip this wait or the post-wait **801B** phase (poses).  
- Pose skip likely needs: shorten/break wait at **16F4**, and/or patch queue type **0xC** at **151C**, and/or hook **801B0000** victory setup.  
- **800F83C6 bit 0x20** is set here every pass — good probe, not the only gate.

## Follow-ups

- [ ] Execute BP **800A16F4** and **800A1700** once post-kill: confirm last 1500-hit is followed by fall-through  
- [ ] Execute BP **801B0000** (enable only after kill): first routines = pose/fanfare  
- [ ] On stop at 151C, note `a1` slot + whether 7254 is what starts win anim  
- [ ] Find outer caller of 800A1158 (stack at entry / jalr site)  
- [ ] Compare train battle: does 16F4 exit immediately or skip 1158?

## Sources

- `docs/first.png` … `docs/7.png`, `docs/INSTRUCTIONS.md`  
- `workspace/iso-extract/BATTLE_X_dec.bin`  
