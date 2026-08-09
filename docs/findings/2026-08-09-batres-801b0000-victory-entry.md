# Finding: 801B0000 is BATRES victory-results entry

**Date:** 2026-08-09
**Status:** confirmed (live step + static overlay)
**Module:** BATTLE/BATRES.X (decoded) @ **0x801B0000**
**Source:** cf52ba3 step shots + `workspace/iso-extract/noswap-re/BATTLE__BATRES.X.dec`

## Live evidence (step ~30)

| Item | Value |
|------|--------|
| Entry BP | **801B0000**, `ra = 800A1734` (win_transition return) |
| Prologue | `addiu sp,sp,-136` then save s2.. |
| Early PC peak | **801B007C** `jal 800A6000` (a1=6,a2=6); loop s1 0..9 |
| End of ~30 steps | **801B0088** `slti s1,10` after first call return (`s1=1`) |
| Flag load | `lui s2,0x8010` / `lhu s2,-0x7C3A(s2)` → **800F83C6** |

Shot pack: `docs/first stop.png` + `docs/image.png` + `docs/image copy*.png` (unordered names; use PC in shot).

## Overlay identity

`BATTLE__BATRES.X.dec` **starts** with the same prologue words as live 801B0000:

`27BDFF78 AFB20068 ...` at file offset **0**.

| VA | File off | Role |
|----|----------|------|
| **801B0000** | 0x0 | victory results / end-of-battle entry (this function) |
| size | 0x193C | full decoded BATRES body available offline |

BATTLE.X does **not** contain this image; BATRES does.

## Static outline (entry fn)

```
801B0000  prologue (big stack frame)
801B000C  s2 = *(u16*)0x800F83C6     ; battle end flags
801B0014  t0 = *(u16*)0x8009D78A     ; saved on sp+0x18
801B0060  for s1 in 0..9:            ; stride s0 += 0x68 actor slots
            if actor_byte != -1:
801B007C     jal 800A6000(a0=idx, a1=6, a2=6)   ; BATTLE.X helper
801B0094  if *(u16*)0x800F83D0 & 4:  copy six words into kernel struct
801B00F8  if *(u16*)0x800F7DD2:      jal 80014A58; accumulate rewards math
801B0200  merge more flags into s2 (0x40/0x80/0x20/0x2/0x8 ...)
801B0278  jal 801B0E20               ; BATRES internal
801B028C  loop jal 800A7254 x10
801B02FC  optional jal 800B1060(a0=8) ; music/CD-ish path candidate
...
801B051C  jal 800A3354
801B0524  nested jal 800A56B0        ; wait/delay style (a0=0xA then 0..2)
801B0558  jal 800DCF94(a0=-1)        ; strong fanfare/SND candidate
```

First **outbound** call from victory path is therefore **BATTLE.X `800A6000`**, not a music call.
Music/fanfare is later in the same BATRES function (candidates **800B1060**, **800DCF94**, plus pose-ish **800A31A0** / **800A3354**).

## Call chain (updated)

```
fun_800A1158 win_transition
  wait 800A16F4 until s1==0xFFFF
  fall 800A1700...
  jal 801B0000          ; BATRES entry  (ra=800A1734)
    loop jal 800A6000   ; per-actor setup (a1=a2=6)
    ... flag/reward ...
    jal 801B0E20 / 800A7254 / ...
    later: 800B1060, 800A56B0, 800DCF94, ...
```

## Next RE targets (priority)

1. Finish stepping BATRES entry past the s1-loop to **801B0278 / 801B02FC / 801B0558**.
2. BP those jals live; note a0-a3 + whether fanfare/pose already started.
3. Static: name **800A6000** in BATTLE_X (already at file+0x6000).
4. Static: follow **800DCF94** / **800B1060** for audio.

## Live follow-up

Late BPs + frozen battle tone:
[2026-08-09-batres-late-jals-stuck-tone](2026-08-09-batres-late-jals-stuck-tone.md).
