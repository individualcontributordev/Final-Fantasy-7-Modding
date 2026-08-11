# Task: Retest disc1 to disc2 (LOST2 break) on single-disc-on-csr v0.1.6

## What was wrong

Disc 1 → “disc 2” freeze / no break scene at the start of disc 2.

**Cause:** CSR D2 **LOST2** break jumps to **cos_btm2**, but an IFUW often
skipped that MAPJUMP on single-disc (disc-id / flag context). You landed on
the forest without the D2 open break.

**Fix:** **single-disc-on-csr-v0.1.6** forces that MAPJUMP (IFUW else-jump 0).
Still includes 0.1.5 post-Hojo Ask strips.

## What you do

1. Hard-refresh the builder  
2. Rebuild Disc 1: **CSR + CSR+ + Single-disc**  
3. Confirm APPLIED.txt shows **single-disc-on-csr-v0.1.6**  
4. **Quit DuckStation fully**, then open the new bin (no save-state for this test)  
5. From an **in-game save** before the disc1→2 transition, run the transition  
6. Expect **break / cos_btm2 routing**, then LOST2 area playable  

Also optional: cold-boot retest post-Hojo → field 744 if you have that save.

## Evidence (fill in)

```
APPLIED single-disc id:
Disc1 to disc2 transition: OK / FREEZE / NO BREAK / OTHER
Break scene / cosmo bottom2: SEEN / MISSING
Field after transition playable?: YES / NO
CSR+ on?: YES/NO
Used save-state?: NO (preferred) / YES
Cold DuckStation boot?: YES/NO
notes:
```

## When done

Pull, paste evidence into this file, commit, push, say **check**.

Commit message example: ops: retest disc1-disc2 LOST2 break after single-disc 0.1.6
