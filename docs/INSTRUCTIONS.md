# Task: No-swap prototype — fix gate bits; only skip Ask

Operational handoff. Agent overwrites this file and pushes.
You: git pull --ff-only, fix Makou script, evidence, commit+push. Say **check**.

## Goal

Same working image: neutralize the four `Ask for disc` ops in **blackbgb**
S0-Main **without** skipping the `Bit … OFF` clears (or save setup).

Prior: `docs/findings/2026-08-02-noswap-blackbgb-ask-skip-proto.md`

Working image (keep using this path):
`workspace/iso-extract/ff7_d1_noswap_re.bin`

## Bug in current edit

Each branch does roughly:

```
Goto label 15
Bit N OFF          ← dead (bad)
Label 15
...
Goto label 11
Ask for disc N     ← dead (good)
Label 11
jump ...
```

**Fix:** Bit OFF must run. Only Ask must be skipped/removed.

## Preferred fix (clean)

In `blackbgb` → `init` → S0-Main, **delete** the four `Ask for disc` lines only.
Remove the extra Goto/Label pairs added for skipping if they are no longer needed.
Restore normal flow:

1. bit-5 path: Bit 5 OFF → wait → (no ask) → music → jump **las0_1 #744**
2. bit-6 path: Bit 6 OFF → cloud/save UI unchanged → (no ask) → music → **las0_1 #744**
3. bit-2 path: Bit 2 OFF → wait → (no ask) → flags/music → **lost2 #634**
4. bit-4 path: Bit 4 OFF → cloud/save UI unchanged → (no ask) → flags/music → **lost2 #634**

## Steps

1. git pull --ff-only
2. Open working ISO in Makou → blackbgb → init → S0-Main
3. Apply preferred fix (delete Asks + clean dead Gotos if easy)
4. Save field into the same working ISO
5. Paste the four disc branches (or full disc section) under Evidence
6. Confirm in paste: each gate still has **Bit … OFF** before the jump; **no**
   live Ask on the fall-through path
7. Commit this file only (no .bin)

## Evidence

```
Working image path:
Ask for disc still present as dead code? (yes/no):
Bit OFF runs on all four disc branches? (yes/no):
```

### Disc section paste (after fix)

```
(paste S0-Main from first disc gate through lost2/las0_1 jumps)
```

## Done when

- Asks not executed; Bit OFFs execute; jumps intact
- Evidence pushed; say **check**

## Out of scope

- Builder pack (next turn after fix verifies)
- blackbg3 / blackbge / multi-disc movie
- CSR / Highwind
