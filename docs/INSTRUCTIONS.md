# Task: Retest post-Hojo to field 744 on single-disc-on-csr v0.1.5

## What was wrong

After the **Hojo** fight, the game froze on **field 744 (las0_1 / Northern Cave)**.

**Cause:** Single-disc used CSR Disc 2 **CANON_2**, which still had **Ask for disc 3**.
That disc-change never finishes on a Disc 1-only image. las0_1 itself was fine.

**Fix:** **single-disc-on-csr-v0.1.5** NOPs residual Ask-for-disc 2/3 on CANON_2
(and several other leftover maps).

## What you do

1. Hard-refresh the builder
2. Rebuild Disc 1: **CSR + CSR+ + Single-disc** (same stack you were testing)
3. Confirm APPLIED.txt shows **single-disc-on-csr-v0.1.5** (not 0.1.4)
4. Fresh DuckStation boot
5. From a save **after Hojo / Sister Ray**, walk the transition into Northern Cave
   (field **744**)

## Evidence (fill in)

```
APPLIED single-disc id:
Post-Hojo transition: OK / FREEZE / OTHER
Field 744 las0_1: OK / FREEZE
CSR+ on?: YES/NO
notes:
```

## When done

Pull latest, fill the evidence block above in this file, commit and push, then say **check**.

Example commit message: ops: retest post-Hojo field 744 after single-disc 0.1.5
