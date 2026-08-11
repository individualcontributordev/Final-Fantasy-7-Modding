# Task: Isolate field 122 (NMKIN_2 stairs) freeze — CSR vs CSR+

## Why

You froze on **field 122** after the elevator stairs with **CSR + CSR+** and **no Single-disc**.

Agent check:

- Field **122 = NMKIN_2** (reactor walkway after ELEVTR1).
- **CSR+ does not modify** NMKIN_2 / ELEVTR1 at all on Disc 1.
- **CSR base also leaves NMKIN_2 stock**, but **does trim NMKIN_1** (and other early reactor maps). Softlock may be bad state from an earlier map, not corrupted 122 data.

We need one cold isolation pass.

## What you do

### Build A — CSR only (control)

1. Hard-refresh the builder
2. Base: **CSR**
3. Mods: **nothing** (no CSR+, no Single-disc, no Fanfare, no encounter packs)
4. Build Disc 1, note zip name
5. **Quit DuckStation fully**, open the new bin (no save-state)
6. Cold boot / new game then bomb mission then elevator then **walk down stairs on field 122**
7. Record: OK or FREEZE

### Build B — CSR + CSR+ only

1. Same as A but enable **CSR+** (all-or-none)
2. Confirm APPLIED.txt has CSR+ scene packs and **no** single-disc
3. Same cold path to field 122 stairs
4. Record: OK or FREEZE

## Evidence (paste below)

```
Build A CSR-only APPLIED (paste or list lines):
field 122 stairs: OK / FREEZE
notes:

Build B CSR+CSR+ APPLIED (paste):
field 122 stairs: OK / FREEZE
notes:
If freeze: music continues? YES/NO
DuckStation FPS 0? YES/NO
Any CD log snippet after freeze (optional):
```

## When done

Commit this file with evidence, push, say **check**.

Commit example: ops: isolate field 122 freeze CSR vs CSR+
