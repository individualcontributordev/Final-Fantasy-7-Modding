# Task: Retest Cosmo WHITE2 on single-disc-on-csr v0.1.4

## What was wrong

Field **643 = WHITE2**. DuckStation showed **MDEC invalid commands**, DMA FIFO
underflows, and **FPS ~0–1** (crawl + graphical glitches).

**Cause:** v0.1.3 put **pure CSR Disc 2** WHITE2 back on Disc 1 and undid the
old **movie trim**. Disc 1 then played the wrong movie streams → MDEC garbage.

**Fix:** **single-disc-on-csr-v0.1.4** restores the trimmed WHITE2 (and LOSLAKE3)
from 0.1.2. Movie pairs on WHITE2 are **0** again.

## What you do

1. Hard-refresh the builder  
2. Rebuild Disc 1: **CSR + Single-disc** (CSR+ optional, same stack as before)  
3. Confirm APPLIED.txt shows **`single-disc-on-csr-v0.1.4`** (not 0.1.3)  
4. Fresh DuckStation boot  
5. Go to Cosmo / Bugenhagen area — especially **field 643 WHITE2**

## Evidence (fill in)

```
APPLIED single-disc id:
Field 643 WHITE2: OK / GLITCH / FREEZE / CRAWL
Field 642 WHITE1: OK / GLITCH
Waterfall / loslake: OK / GLITCH
CSR+ on?: YES/NO
DuckStation MDEC/DMA spam?: NO / YES
notes:
```

## When done

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
git add docs/INSTRUCTIONS.md
git commit -m "ops: retest Cosmo WHITE2 after single-disc 0.1.4"
git push
```

Then say **check**.
