# Task: Rebuild CSR+ single-disc after apply-order fix

## What went wrong

CSR+ disc1 layers must be applied **after** Single-disc. Older builds could apply
CSR+ earlier and corrupt the image (glitch on early fields, softlock after elevator
with music still playing).

Builder now forces order: Single-disc first, CSR+ last.

Finding: docs/findings/2026-08-11-single-disc-csrplus-early-freeze-layer-order.md

## What you do

1. Hard-refresh https://individualcontributor.dev/builder/
2. Rebuild Disc 1: Base CSR, mods Single-disc + CSR+ (optional enc/fanfare)
3. Open APPLIED.txt — Single-disc should appear **before** CSR+ scene packs
4. Fully quit DuckStation, reopen
5. Play through first reactor / elevator stretch

### Optional bisect if still broken

- A: CSR only
- B: CSR + Single-disc (no CSR+)
- C: CSR + Single-disc + CSR+

## Evidence

```
Hard-refresh builder: YES/NO
APPLIED order (after base, first few mods):
Early fields / elevator: OK / GLITCH / FREEZE
Softlock music continues?: YES/NO
After full DS quit+reopen same?: YES/NO

If failed:
A CSR only:
B CSR+SD:
C full:
notes:
```

## When done

```bash
cd "$(git rev-parse --show-toplevel)"
git pull --ff-only
git add docs/INSTRUCTIONS.md
git commit -m "ops: retest CSR+ SD after layer apply order fix"
git push
```

Then say **check**.
