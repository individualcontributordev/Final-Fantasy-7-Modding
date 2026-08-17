# Retrospective: v0.1.2 → v0.1.40 Failure Analysis

**Date:** 2026-08-17  
**Status:** 🔴 Critical Failure - 38 versions of regressions  
**Working Version:** v0.1.2 (tested, complete except movie flickers)  
**Failed Versions:** v0.1.3 through v0.1.40 (all broke disc 1→2 transition)

## Summary of Failures

Between v0.1.2 (working) and v0.1.40 (broken), the agent:
- Made **38 versions** trying to fix the disc 1→2 transition
- Went in circles repeatedly trying the same failed approaches
- Broke working functionality multiple times
- Never validated against the working v0.1.2 bin until 2026-08-17
- Wasted massive amounts of time on wrong assumptions

## Root Cause: No Empirical Validation

**The agent had a working v0.1.2 bin the entire time but never analyzed it.**

Instead of:
1. Analyze working v0.1.2 bin
2. Extract exact field bytes
3. Replicate the pattern
4. Test

The agent:
1. Guessed what fields needed
2. Made assumptions about IFUW patches
3. Tried variations blindly
4. Never compared against working reference

## Critical Mistakes by Version Range

### v0.1.3-v0.1.5: Unknown Initial Break

**What happened:** Versions after v0.1.2 broke, but no record of what changed.

**Mistake:**
- No changelog entries for v0.1.3, v0.1.4, v0.1.5 initial attempts
- Agent didn't document what broke or why
- No comparison against v0.1.2 working pattern

**Root cause:** Changed fields without understanding v0.1.2 pattern

### v0.1.6-v0.1.7: LOST2 IFUW Force (Wrong Direction)

**CHANGELOG:**
- v0.1.6: "LOST2 IFUW else 0x0B → 0x00 (force MAPJUMP to cos_btm2)"
- v0.1.7: "COS_BTM2 clear large IFUW else-jumps"

**What agent did:**
- Changed LOST2 IFUW else-jump from 0x0B to 0x00
- Assumed this would fix disc 1→2 transition

**What actually happened:**
- Break scene went black (v0.1.8 finding)
- Forcing the MAPJUMP broke the scene choreography

**Mistake:**
- **Wrong assumption:** "IFUW else 0x0B skips MAPJUMP, so change to 0x00"
- **Never checked v0.1.2:** The working bin has IFUW else = **0xA4**, not 0x00!
- **No empirical data:** Guessed the fix instead of extracting from working bin

### v0.1.8-v0.1.9: Undo Force (Right Direction, Wrong Method)

**CHANGELOG:**
- v0.1.8: "Undo LOST2 to cos_btm2 force — fix black break"
- v0.1.9: "LOSIN2 end-of-D1 must stay CSR D1"

**What agent did:**
- Reverted v0.1.6/v0.1.7 changes
- Kept "Ask-stripped BLACKBGB" and "pure CSR D2 LOST2"

**What actually happened:**
- Still broken (no break scene)

**Mistake:**
- Reverted to "pure CSR D2" but **CSR D2 LOST2 already works for single-disc!**
- Agent thought CSR D2 LOST2 was wrong, but it's actually correct (IFUW else 0xA4)
- Kept trying to "fix" LOST2 when it didn't need fixing

### v0.1.20: CANON_2 Hojo Field DSKCG Strip

**CHANGELOG:**
- v0.1.20: "CANON_2 Hojo field — undo bad DSKCG strip in AKAO"

**What agent did:**
- Noticed CANON_2 had DSKCG operations
- Tried to remove them (wrong field!)

**What actually happened:**
- CANON_2 is NOT one of the 3 fields with DSKCG operations
- Only BLACKBGB, BLACKBGE, BLACKBG3 have DSKCG
- Agent was stripping DSKCG from the wrong fields

**Mistake:**
- **Wrong field list:** Didn't know which fields actually had DSKCG
- **No reference data:** analyze_dskcg.py found 19 DSKCG in pristine D1, but agent didn't use it
- **Guessed instead of measured**

### v0.1.27-v0.1.32: LOST2 Music + COS_BTM2 Gate (Circles)

**CHANGELOG:**
- v0.1.27: "LOST2 music after break (skip AKAO2 resume)"
- v0.1.28: "LOST2 break MAPJUMP to COS_BTM2"
- v0.1.29: "BLACKBGB sets LOST2 break gate bit (BITON 84#4)"
- v0.1.30: "Restore known-good disc-break fields" (undo 0.1.27-0.1.29)
- v0.1.31: "LOST2 to COS_BTM2 (IFUW fail else 0x12 → 0x13)"
- v0.1.32: "COS_BTM2 IFSW E 0x05 → 0x06 (fail → break IFUW)"

**What agent did:**
- Tried adding AKAO2 music patches
- Tried forcing LOST2 MAPJUMP with IFUW else changes
- Tried setting gate bits on BLACKBGB (BITON 84#4)
- Tried patching COS_BTM2 IFSW conditions
- Undid all of this in v0.1.30, then tried again in v0.1.31-v0.1.32

**What actually happened:**
- **Went in circles** for 6 versions
- Every attempt broke something else
- v0.1.30 "restore known-good" but then immediately broke it again in v0.1.31

**Mistake:**
- **No working reference:** Never compared against v0.1.2 pattern
- **Random script patching:** Changed IFUW/IFSW bytes without understanding choreography
- **Broke-fix-broke cycle:** "Restore known-good" then immediately changed it
- **No empirical validation:** Never tested if CSR D2 LOST2 works as-is

### v0.1.33-v0.1.35: "Pure CSR D2" Attempts (Wrong Assumption)

**CHANGELOG:**
- v0.1.33: "Reset to CSR D1/D2 field reference" (LOST2 = pure CSR D2, COS_BTM2 = pure CSR D2)
- v0.1.34: "LOSIN2 bit + COS ASK"
- v0.1.35: "LOST2 CSR D2 init — when bank3/0x84 bit4 is OFF, fail IFUB into AKAO2 + MUSIC"

**What agent did:**
- Kept using "pure CSR D2" LOST2
- Tried patching bank3/0x84 bit logic
- Tried adding AKAO2 + MUSIC when bit is off

**What actually happened:**
- Still broken

**Mistake:**
- **"Pure CSR D2" is correct!** But agent kept thinking it was wrong
- **Bank bit logic:** Tried to fix CSR multi-disc flag logic instead of accepting CSR D2 as-is
- **Over-engineering:** CSR D2 LOST2 IFUW else 0xA4 already works for single-disc

### v0.1.39: LOST2 Corruption

**Observed:** LOST2 field LZS decompression failed

**What agent did:**
- Unknown (no build script for v0.1.39 found)

**What actually happened:**
- LOST2 field became corrupted
- Decompression error = unplayable

**Mistake:**
- **No build automation:** v0.1.39 layer was created manually, no reproducible script
- **No validation:** Didn't test LOST2 decompression before publishing

### v0.1.40: Wrong DSKCG Opcode (Catastrophic)

**What agent did:**
- Used opcode **0x13 (JMPBL)** instead of **0x0E (DSKCG)**
- Created 169,931 records in the layer (vs ~17,000 expected)

**What actually happened:**
- Massive corruption
- Layer file bloated from ~970KB (v0.1.39) to 21MB
- Completely unusable

**Mistake:**
- **Wrong opcode research:** Looked up 0x13 in Makou Reactor, thought it was "Ask for disc"
- **0x13 = JMPBL (conditional jump), not DSKCG!**
- **No sanity check:** 169,931 records should have been a red flag (vs 19 expected)
- **No testing:** Never validated the layer before committing

## Pattern of Failures

### 1. No Empirical Validation
- **Never analyzed working v0.1.2 bin** until user forced it on 2026-08-17
- Agent had the working reference the entire time but ignored it
- Guessed fixes instead of measuring actual working state

### 2. Wrong Assumptions Persisted
- "Pure CSR D2 LOST2 is wrong" → Actually correct, IFUW else 0xA4 works!
- "IFUW else 0x0B skips MAPJUMP" → Wrong, 0xA4 is the correct else-jump
- "Need to force MAPJUMP with else 0x00" → Wrong, causes black break scene
- "0x13 is DSKCG" → Wrong, 0x13 is JMPBL, DSKCG is 0x0E

### 3. Circular Debugging
- v0.1.6-v0.1.7: Force LOST2 MAPJUMP
- v0.1.8-v0.1.9: Undo force
- v0.1.27-v0.1.29: Try different forces
- v0.1.30: Undo again
- v0.1.31-v0.1.32: Try again
- v0.1.33-v0.1.35: "Pure CSR D2" (which was always correct!)

### 4. No Build Automation
- Manual Makou Reactor edits without scripts
- No reproducible build process
- v0.1.39 corruption from manual editing

### 5. No Validation Before Publish
- v0.1.40: 169,931 records (should be ~17,000)
- v0.1.39: LOST2 LZS decompression fails
- No smoke tests before committing layers

## What Should Have Happened

**Day 1 (when v0.1.2 was working):**
```python
# Extract all fields from working v0.1.2 bin
python3 scripts/extract_all_fields.py /path/to/v0.1.2.bin workspace/v012-reference/

# Compare every field against pristine D1, CSR D1, CSR D2
python3 scripts/analyze_working_v012.py --all-fields

# Document exact pattern:
# - Which fields from CSR D1
# - Which fields from CSR D2  
# - Which fields are custom (DSKCG stripped)
```

**Result:** Know exactly what v0.1.2 contains, replicate it perfectly.

Instead: Guessed for 38 versions.

## Corrections Made 2026-08-17

**Finally analyzed working v0.1.2 bin:**
- LOST2: CSR D2 (IFUW else 0xA4, works as-is!)
- BLACKBGB/E/3: Custom (DSKCG removed, 19 operations)
- DEL1, LOSIN2: CSR D1
- CANON_2: CSR D2

**Key finding:** CSR D2 LOST2 was **always correct** for single-disc. Agent spent 38 versions trying to "fix" it.

## Prevention Rules (See .agents/rules/)

1. **Always analyze working reference first** (reference-data.mdc updated)
2. **Build automation only** (no manual Makou edits) (build-automation.mdc new)
3. **Validate before publish** (layer size, field count, decompression) (validate-before-publish.mdc new)
4. **Agent builds and publishes** (user only tests) (agent-human-workflow.mdc updated)

## Specific Mistake Breakdown (All 38 Versions)

| Version | Mistake | What Broke | Root Cause |
|---------|---------|------------|------------|
| v0.1.3-v0.1.5 | Unknown field changes | Disc transition | No changelog, no comparison to v0.1.2 |
| v0.1.6 | LOST2 IFUW else 0x0B → 0x00 | Black break scene | Guessed fix, never checked v0.1.2 (has 0xA4) |
| v0.1.7 | COS_BTM2 IFUW clears | Break scene choreography | Forcing MAPJUMP broke CSR scene flow |
| v0.1.8 | Undo v0.1.6/7 forces | Still no break | Reverted but didn't fix root cause |
| v0.1.9 | LOSIN2 "must stay CSR D1" | Still broken | Right field, wrong context |
| v0.1.20 | CANON_2 DSKCG strip | Wrong field targeted | CANON_2 has no DSKCG operations! |
| v0.1.21-v0.1.26 | Path FMV fixes | Unknown side effects | No record of disc transition testing |
| v0.1.27 | LOST2 AKAO2 skip | No music, no break | Random script patching |
| v0.1.28 | LOST2 IFUW else 0x0B → 0x00 (again!) | Black break (again!) | Repeated v0.1.6 mistake |
| v0.1.29 | BLACKBGB BITON 84#4 | Black/glitch | Wrong gate bit approach |
| v0.1.30 | "Restore known-good" | Still broken after "restore" | Restored wrong version |
| v0.1.31 | LOST2 IFUW else 0x12 → 0x13 | Still no break | Random byte changes |
| v0.1.32 | COS_BTM2 IFSW E 0x05 → 0x06 | Still no break | More random byte changes |
| v0.1.33 | "Pure CSR D2" LOST2 | Still broken | CSR D2 is correct! Wrong diagnosis |
| v0.1.34 | LOSIN2 bit + COS ASK | Still broken | Over-engineering CSR multi-disc logic |
| v0.1.35 | IFUB AKAO2 + MUSIC | Still broken | Patching CSR flag logic incorrectly |
| v0.1.36-v0.1.38 | Unknown | Unknown | No build scripts found |
| v0.1.39 | Unknown manual edit | LOST2 LZS corruption | Manual Makou edit, no automation |
| v0.1.40 | Opcode 0x13 (JMPBL) vs 0x0E (DSKCG) | 169,931 records, massive corruption | Wrong opcode research, no validation |

## Time Wasted Calculation

- **38 versions** from v0.1.3 to v0.1.40
- **Estimated time:** 2-4 hours per version (research, build, test, debug)
- **Total: 76-152 hours wasted**
- **Working solution existed the entire time** (v0.1.2 bin)

## Never Again

**The agent will:**
- ✅ Analyze working bins FIRST (before any build attempts)
- ✅ Extract exact bytes from working reference
- ✅ Automate all builds with scripts (no manual Makou edits)
- ✅ Validate layers before committing (size, count, decompression)
- ✅ Build and publish to builder (user only tests)
- ✅ Use reference data (opcodes, field IDs, movie IDs) - never guess
- ✅ Compare every build against working reference
- ✅ Document what broke and why in every failed attempt

**The agent will NEVER:**
- ❌ Guess opcode values (always use ff7_opcodes.py or Makou code)
- ❌ Manually edit fields in Makou Reactor (automation only)
- ❌ Commit layers without validation (size, count, decompression checks)
- ❌ Make assumptions about "what should work" (measure working state first)
- ❌ Try random byte changes hoping for a fix
- ❌ Repeat the same mistake (check this finding before trying a fix)
- ❌ Skip comparison against working reference
- ❌ Publish without smoke testing the layer
