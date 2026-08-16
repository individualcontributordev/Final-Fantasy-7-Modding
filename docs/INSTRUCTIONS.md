# INSTRUCTIONS — Single-Disc Disc 1→2 Transition Fix

## 🔬 NEW FINDING: BLACKBGB Has No MAPJUMP on Pristine

**Analyzed pristine BLACKBGB.DAT from both Disc 1 and Disc 2:**
- ✅ MUSIC opcodes present (in cloud/script31)
- ❌ **NO MAPJUMP opcodes at all**

This means the MAPJUMP #634 we see in single-disc is **added by CSR**, not from the base game!

On pristine multi-disc, BLACKBGB is a simple "disc swap hub" that probably shows a message, then the game's kernel/CD code handles the disc transition automatically.

---

## Current Status: ⏸️ WAITING FOR USER TEST

You reported that **CSR + Single-disc** has issues:
- ✅ Disc 1→2 transition loads field 634 (LOST2 forest)
- ❌ Missing break scene at start of Disc 2
- ❌ No music on field 634

The expected flow on **CSR multi-disc** should be:
1. End of D1: LOSIN2 (field 632) → asks for Disc 2
2. Start of D2: BLACKBGB hub → **COS_BTM2 break scene (field 526)**
3. After break: **LOST2 forest (field 634) with music**

On **CSR + Single-disc**, the flow is:
1. End of D1: LOSIN2 → transition
2. ❌ **Goes directly to field 634**, skipping COS_BTM2 (field 526)
3. ❌ **No music** on field 634

---

## Root Cause (from CHANGELOG v0.1.33-0.1.35)

**Current single-disc state (v0.1.33 core):**
- LOSIN2 = CSR Disc 1 (sets GM=0xa455, **clears** bit4)
- BLACKBGB = Ask-stripped (DSKCG removed)
- LOST2 = **pure CSR Disc 2**
- COS_BTM2 = pure CSR Disc 2

**The problem:**

> Pure CSR D2 LOST2 never MAPJUMPs COS_BTM2 after LOSIN2: LOSIN2 sets GM 0xa455 and BITOFFs bank3/0x84#4, so LOST2 init RETs (no break, no music path).

On **CSR multi-disc**, when you swap from Disc 1 to Disc 2:
- Disc 2 has different initialization code that sets bit4
- LOST2 on D2 checks bit4 and forwards to COS_BTM2 when set
- On **single-disc**, there's no disc swap, so bit4 stays cleared → LOST2 just RETurns

**From v0.1.35 finding:**

> BLACKBGB disc-2 arms still run MAPJUMP #634 then MUSIC id=3 — MUSIC is after MAPJUMP (never runs on hub).

So BLACKBGB is jumping to LOST2 (#634), but LOST2 can't forward to the break scene because the flag isn't set.

**Questions we need answered by testing CSR multi-disc:**
1. What does BLACKBGB do on actual Disc 2? Jump to #526 or #634?
2. If it jumps to #634, how does LOST2 know to forward to COS_BTM2?
3. Where does the break scene actually happen - is it a cutscene in COS_BTM2?

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
