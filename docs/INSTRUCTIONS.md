# Task: Break on late BATRES jals (music/pose candidates)

## Why

Your step pack (`cf52ba3`) + offline decode show:

- **801B0000** = start of **`BATTLE__BATRES.X.dec`** (victory results overlay)
- First work is a **10x** loop: `jal **800A6000**` with `a1=a2=6` (actor slots, stride 0x68)
- After ~30 steps you were still inside that loop (PC ~801B0088, s1=1)
- Fanfare/pose is **later** in the same function. Static candidates:

| VA | Call | Why interesting |
|----|------|-----------------|
| **801B0278** | jal **801B0E20** | BATRES-internal after flag merge |
| **801B02FC** | jal **800B1060**(a0=8) | optional path — music-ish |
| **801B0458** | jal **800A31A0** | pose-ish candidate |
| **801B051C** | jal **800A3354** | repeated with waits |
| **801B0558** | jal **800DCF94**(a0=-1) | strong fanfare/SND candidate |

Finding: `docs/findings/2026-08-09-batres-801b0000-victory-entry.md`

You do **not** need another 30-step photo dump of the prologue loop.

## What you do

### 1. Pull

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
```

### 2. Breakpoints (clean set)

**Remove:** 801B0008, 801B000C (spam / early).

**Keep optional:** 801B0000 only if you want one shot to arm the rest (or arm before last hit).

**Add execute BPs:**

1. **801B0278**
2. **801B02FC**
3. **801B0458**
4. **801B0558**
5. Optional: **800DCF94**, **800B1060**, **800A31A0** (callees)

Still **do not** enable 800D3098 / 800A54A0 unless a BP never hits and you need a safety net.

If a late BP never hits on a kill, note which flag bits you had (s2 / F83C6) — paths are flag-gated.

### 3. Fight

- Fanfare Skip 0.1.4, HUD up, save before last kill
- Kill last enemy
- For **each** BP that hits: one screenshot (or fill Evidence). Note if fanfare/pose already audible/visible.

### 4. Optional rename shots

Prefer names like `docs/801B0278.png` so we are not guessing `image copy N`.

## Evidence

```
BP hit list (in order):
801B0278: HIT/MISS  ra=  a0= a1= a2= a3=  s2=  moment:
801B02FC: HIT/MISS  ra=  a0= ...  moment:
801B0458: HIT/MISS  ...
801B0558: HIT/MISS  ...
800DCF94 (if used): ...
800B1060 (if used): ...

Which BP is first AFTER fanfare becomes audible? (or NEVER sure)
Which BP is first AFTER victory pose starts? (or NEVER sure)
```

## When done

```bash
git add docs/INSTRUCTIONS.md docs/*.png 2>/dev/null || git add docs/INSTRUCTIONS.md
git commit -m "ops: BATRES late jal BP evidence (music/pose)"
git push
```

Then say **check**.
