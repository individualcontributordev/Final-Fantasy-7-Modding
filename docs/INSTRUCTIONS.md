# INSTRUCTIONS — Single-Disc Disc 1→2 Transition Analysis

## Problem Report

You tested **CSR + Single-disc** and found:
- ✅ Disc 1→2 transition loads field 634 (LOST2 forest)
- ❌ Missing break scene at start of Disc 2
- ❌ No music on field 634

On **CSR multi-disc**, the correct flow should be:
1. End of D1: LOSIN2 (field 632) → asks for Disc 2
2. Start of D2: BLACKBGB hub → **COS_BTM2 break scene (field 526)**
3. After break: **LOST2 forest (field 634) with music**

On **CSR + Single-disc**, the flow is:
1. End of D1: LOSIN2 → transition
2. ❌ **Goes directly to field 634**, skipping COS_BTM2 (field 526)
3. ❌ **No music** on field 634

---

## Root Cause (from findings)

From `docs/findings/2026-08-13-v035-music-fail-save-ok.md`:

> BLACKBGB disc-2 arms still run MAPJUMP #634 then MUSIC id=3 — MUSIC is after MAPJUMP (never runs on hub). Save arm is the one playtest hit.

**Two bugs:**
1. **BLACKBGB jumps to wrong field:** Should MAPJUMP #526 (COS_BTM2 break), but jumps to #634 (LOST2) instead
2. **MUSIC after MAPJUMP:** Even if it jumped correctly, MUSIC opcode comes after MAPJUMP so it never plays

---

## Analysis Needed

Before creating a fix, I need to confirm the expected behavior.

### Test: CSR Multi-Disc Behavior

On Windows, test a clean CSR multi-disc build (D1 + D2, NO single-disc) to see what actually happens:

1. **Build CSR discs** (NO mods):
   - Go to https://individualcontributor.dev/builder/
   - Select "Base Experience: CSR v0.14.1"
   - Select "Disc 1", click "Build Disc 1"
   - Save the .zip, extract, get the .bin
   - Select "Disc 2", click "Build Disc 2"  
   - Save the .zip, extract, get the .bin

2. **Load in DuckStation:**
   - Load CSR Disc 1 .bin
   - Play to end of Disc 1 (or load a save state near the disc break)

3. **At "Please insert Disc 2" prompt:**
   - In DuckStation: "System" → "Change Disc" → select CSR Disc 2 .bin
   - Continue

4. **Record what happens:**
   - What field loads? (You can watch field ID in Cheat Engine: `DuckStation.exe+7F1600+0x11C2A4`, 2-byte hex)
   - Do you see any cutscene/dialogue at Cosmo Canyon?
   - Do you hear music when you reach the forest?
   - Can you move and play normally?

### Paste Here

**CSR multi-disc test results:**
- Field ID when D2 starts: ____
- Break scene at Cosmo: YES / NO / (describe what you saw)
- Music in forest: YES / NO
- Able to continue playing: YES / NO

---

## Next: Fix After Confirmation

Once you confirm the CSR multi-disc behavior, I will create **v0.1.36** that:

1. Patches BLACKBGB to MAPJUMP #526 (break scene) instead of #634
2. Moves MUSIC before MAPJUMP so it actually plays
3. Ensures break scene works on single-disc

---

## Hold

No code changes yet. Run the CSR multi-disc test above, paste results here, then say **check**.
