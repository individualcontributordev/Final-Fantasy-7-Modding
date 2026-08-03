# No-disc-swap — blackbgb Ask skip prototype (pristine D1)

**Date:** 2026-08-02
**Confidence:** confirmed (script paste after Makou edit)
**Working image (operator):** `workspace/iso-extract/ff7_d1_noswap_re.bin`
  (Windows path: `D:\projects\Final-Fantasy-7-Modding\workspace\iso-extract\ff7_d1_noswap_re.bin`)

## Intent

Skip the four `Ask for disc` ops in `blackbgb` / `init` / S0-Main; keep jumps
to `las0_1` (#744) and `lost2` (#634).

## What was done

Each disc branch uses `Goto label N` **over** the Ask line so Ask is unreachable,
then resumes music/wait/jump. Example (disc 3, bit-5 path):

```
If Var[3][136] bitON 5 (else goto label 3)
        Goto label 15
        Bit 5 OFF in Var[3][136]    # NEVER RUNS
        Label 15
        Wait 4 frame
        Goto label 11
        Ask for disc 3              # never runs (good)
        Label 11
        Play music #2
        ...
        Jump to map las0_1 (#744)
```

Same pattern on all four branches (labels 11–14 skip Ask; labels 15–18 skip
leading Bit OFF / gate clear).

## Result

| Goal | Status |
|------|--------|
| Ask not executed | **OK** (dead code after Goto) |
| Jump targets kept | **OK** (las0_1 / lost2 unchanged) |
| Gate bits cleared | **BUG** — `Bit N OFF` sits **between** `Goto label 15/16/17/18` and the label, so clears never run |

## Why the bit-clear bug matters

Direct disc branches rely on clearing the entry bit (`Var[3][136]` bits 5/4,
`Var[3][134]` bit 2, `Var[13][82]` bit 6). If the bit stays ON and the player
re-enters `blackbgb`, the same branch fires again (instant re-jump / soft lock
loop risk). Save-prompt branches still clear some bits later; the **direct**
resume paths are the worst case.

## Correct prototype shape

For each disc branch, keep original order except **only** skip/delete Ask:

```
Bit X OFF in Var[...]     # MUST run
Wait ...
# no Ask for disc
Play music / Wait
Jump to map ...
```

Prefer **delete** the four Ask ops in Makou (cleanest). If using Goto, jump
**from immediately before Ask to immediately after Ask** only — do not jump
over Bit OFF or save UI setup.

## Asks still visible in script text

Find All may still list `Ask for disc` as dead instructions. That is fine for a
skip-based patch; after a clean delete they should be gone entirely.

## Next

1. Fix the four branches (keep Bit OFF; only neutralize Ask).
2. Re-paste S0-Main disc section for verify.
3. Then diff working ISO vs pristine → `FIELD/blackbgb` (and side files) layer.
