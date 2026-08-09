# Task: When does the battle tone freeze? (relative to BATRES jals)

## Why

Evidence from your push (`4c347fb`) is good:

| BP | Hit? | Meaning |
|----|------|---------|
| 801B0000 | yes | BATRES entry (ra=800A1734) |
| 801B0278 | yes | jal 801B0E20; s2=**0x20** |
| 801B02FC | **no** | expected — needs other flag bits |
| 801B0458 | yes | jal 800A31A0(0,0,0,0); you: near end of fanfare window |
| 801B0558 | yes | jal **800DCF94(-1)** = clear flag @800F1E4F, **not** play song |

**Your audio note (accepted):** after entering victory via 801B0000, battle SFX later die into a **held single tone** until world map; **not** caused by parking on the 801B0000 BP (frames pass first).

That sounds like **BGM/SPU not torn down or not retargeted**, not FAN2 playing. Fanfare Skip 0.1.4 already stubs victory-queue **800A2974** + quiets FAN2 — freeze may be side-effect of missing stock handoff.

Finding: `docs/findings/2026-08-09-batres-late-jals-stuck-tone.md`

We only need **when** freeze starts vs the three hits. No giant step dumps.

## What you do

### 1. Pull

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
```

### 2. Breakpoints

**Remove:** 801B02FC (will miss again on this path).

**Use one kill per mode** (reload save as needed):

**Mode A — stop at 0278**
- Enable only **801B0278**
- Kill last enemy; when it hits: listen 1–2s while **paused**, then note if freeze already started **before** this stop (i.e. during run-up after kill). Continue; listen after resume.

not before 801B0278
freeze happens after continuing from here 801B0278

**Mode B — stop at 0458**
- Only **801B0458**
- Same listen: freeze already on when you land? or only after continue past 0458?

sound freeze happens before 801B0458 bp hits

**Mode C — stop at 0558**
- Only **801B0558** (jal 800DCF94 -1)
- Freeze already on at arrival? or only after stepping the jal / continuing?

freeze already on here at 801B0558

**Mode D — optional control (if time)**
- Same fight on **stock** ISO (no fanfare-skip) OR disable 800A2974 patch only if you know how — write NEVER if skip.
- Does the held-tone still happen?

using stock ISO the sound does not freeze at all verified


Do **not** need 801B0000 BP for A–C (lets audio run). Optional safety: 801B0000 disabled.

### 3. Fight setup

Same as always: Fanfare Skip 0.1.4 for A–C, HUD up, save before last hit.

## Evidence

```
Mode A 0278:
  freeze already when BP hit? YES/NO/UNSURE
  freeze after continue past 0278 before next ceremony stuff? YES/NO/UNSURE
  shot: (optional)

Mode B 0458:
  freeze already when BP hit? YES/NO/UNSURE
  freeze only after continue? YES/NO/UNSURE
  shot:

Mode C 0558:
  freeze already when BP hit? YES/NO/UNSURE
  freeze only after jal 800DCF94 / continue? YES/NO/UNSURE
  a0 still -1? 
  shot:

Mode D stock/control:
  held tone happens? YES/NO/NEVER
  notes:

Earliest BP arrival where freeze is ALREADY audible:
  0278 / 0458 / 0558 / only AFTER 0558 / UNSURE
```

## When done

```bash
git add docs/INSTRUCTIONS.md docs/*.png 2>/dev/null || git add docs/INSTRUCTIONS.md
git commit -m "ops: freeze timing vs BATRES 0278/0458/0558"
git push
```

Then say **check**.
