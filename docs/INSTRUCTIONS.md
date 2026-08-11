# Task: Retest Cosmo / Bugenhagen on single-disc-on-csr v0.1.3

## What was wrong

Field **642 = WHITE1** (Cosmo). WATERFALL = loslake*.  

v0.1.2 left **hybrid** scripts (`WHITE2`, `LOSLAKE3`, …) that were not pure CSR D1 or D2 → glitches in that area even when early Midgar was fine.

## Fix shipped

**single-disc-on-csr-v0.1.3** — Cosmo corridor maps restored from pure CSR Disc 2.  
Hard-refresh builder. 0.1.2 is disabled.

Also keep apply order: Single-disc before CSR+ (previous fix).

## What you do

1. Hard-refresh builder  
2. Rebuild Disc 1: CSR + Single-disc (+ CSR+ if you want same stack)  
3. Confirm APPLIED.txt shows **single-disc-on-csr-v0.1.3** (not 0.1.2)  
4. Fresh DuckStation; go to Cosmo / Bugenhagen waterfall + field 642 (WHITE1)

## Evidence

```
APPLIED single-disc id:
Cosmo waterfall: OK / GLITCH / FREEZE
Field 642 WHITE1: OK / GLITCH / FREEZE
CSR+ on?: YES/NO
notes:
```

## When done

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
git add docs/INSTRUCTIONS.md
git commit -m "ops: retest Cosmo after single-disc 0.1.3"
git push
```

Then say **check**.

