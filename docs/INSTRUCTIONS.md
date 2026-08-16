# Agent Task: Single-Disc D1→D2 Break Scene Investigation

## Current Status

**Problem:** Single-disc skips the Cosmo Canyon break scene and has no music after the D1→D2 transition.

**Root Cause Identified:**
- CSR multi-disc relies on `bank3[0x84]` bit4 being set during disc swap
- LOST2 (D2) init script checks bit4 before jumping to COS_BTM2 break scene
- Single-disc never sets bit4 (no physical disc swap), so LOST2 RETs early

## Investigation Findings

### Database Analysis Complete
Built SQLite database at `docs/reference/field-scripts.db` with CSR and pristine field scripts:

```bash
# Query examples
python scripts/query_field_scripts.py --field LOST2
python scripts/query_field_scripts.py --opcode MAPJUMP
```

**Key Findings:**
1. **LOST2 CSR D2** init script (268 bytes total):
   - Raw hex: `430014308404091c1820000055a40112da...`
   - Contains reference to field #526 at offset 0x46: `0e 02` (COS_BTM2)
   - BUT: This is NOT in a MAPJUMP opcode - it's embedded in parameters
   - The actual flow logic is more complex than expected

2. **LOSIN2** (end of D1):
   - No `BITOFF bank3[0x84]` found in pristine OR CSR
   - The bit manipulation must happen elsewhere or be disc-init code

3. **BLACKBGB** (disc swap trigger):
   - No MAPJUMP opcodes in pristine or CSR
   - Transition logic added by CSR in a way not visible in our field script database

### Attempts Made

**v0.1.34 (disabled):** Malformed offset-based layer with 544 empty-path records
**v0.1.35 (disabled):** Incomplete, no pack.json
**v0.1.36 (disabled):** Similar malformed state
**v0.1.37 (enabled but broken):** Tried to patch LOSIN2 BITOFF→BITON, but byte pattern not found

**Current Manifest State:**
- ✓ single-disc-on-csr-v0.1.33 (core, enabled)
- ✗ single-disc-on-csr-v0.1.34 (auto fix, disabled)
- ✗ single-disc-on-csr-v0.1.35 (disabled)
- ✗ single-disc-on-csr-v0.1.36 (disabled)  
- ✓ single-disc-on-csr-v0.1.37 (enabled but empty fix)

## What You Need to Do

### 1. Test Current CSR Multi-Disc Behavior

Build a clean CSR multi-disc set and play through the D1→D2 transition:

```bash
cd ~/Final-Fantasy-7-CSR
# Follow CSR build instructions to create discs
# Load save at Cosmo Canyon before rocket launch
# Play through rocket sequence → disc swap → observe
```

**Record:**
- Does the break scene play?
- What music plays in LOST2 forest after?
- Any visual glitches or black screens?

### 2. Decode LOST2 Init Script Properly

The raw bytes at offset 0x3D-0x50 need proper decoding:

```
0x3d: 18 20 00 00 55 a4 00 0b 60 0e 02 7b ff 1c fa 65 00 e0 16
```

**Questions:**
- What is opcode 0x18? (Might be IFUB/IFUW with different encoding)
- The `0e 02` at 0x46 is field #526 - what opcode uses it?
- What does `0b` at offset 0x44 control? (else-offset?)

**Tools to use:**
- Makou Reactor (open LOST2.DAT directly)
- Black Chocobo save editor (set GM to 0xa455 for testing)
- Compare pristine vs CSR LOST2 byte-by-byte

### 3. Find the Actual Bit Flag

Search CSR executable or disc-init code for bank3[0x84] manipulation:

```bash
# In CSR repo if you have SLUS decompressed
strings SLUS_014.46 | grep -i "bank\|0x84"

# Or search in Ghidra (if you have the project)
```

### 4. Simpler Fix Approach

Instead of finding the exact bit, try **bypassing the check entirely**:

**Option A:** Patch LOST2 to always jump to COS_BTM2
- Find the conditional jump that checks bit4
- Replace with unconditional MAPJUMP to field #526

**Option B:** Force bit4 ON at game start
- Patch BLACKBGB or game init to set `bank3[0x84]#4 = 1`
- This mirrors what disc-swap does

**Option C:** Use v0.1.31 approach (from CHANGELOG)**
> LOST2 init IFUW !=0xa455 fail else 0x12 to 0x13 lands MAPJUMP #526

This suggests changing an `else` offset byte to shift the jump target.
- Find offset 0x12 in the init script
- Change to 0x13
- Test if this reaches the MAPJUMP

## Questions for Me

When you test and gather evidence, tell me:

1. **CSR multi-disc test results** - does break scene work?
2. **LOST2 script structure** - what does Makou show for init/script0?
3. **Byte pattern search** - can you find `83 03 84 04` (BITOFF bank3[0x84]) anywhere in CSR D1/D2?
4. **v0.1.31 patch** - where exactly is the byte `0x12` that should become `0x13`?

I'll use your evidence to create the correct fix.

## Context Files

- `docs/reference/disc-transition-knowledge-base.md` - Current findings
- `mods/single-disc/CHANGELOG.md` - History of attempts (v0.1.31-v0.1.36)
- `docs/findings/2026-08-14-break-losin2-bit-and-cos-ask.md` - v0.1.31 gate details

---

**Agent Note:** This task requires human investigation with tools I can't run (Makou Reactor, DuckStation, disc burning). Once you provide the evidence, I can create the exact byte patches needed.
