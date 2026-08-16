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

### 2. LOST2 Init Script DECODED ✅

Built CSR D1 bin and analyzed LOST2. Using `scripts/decode_field_script.py`:

**CSR D1 LOST2 init @ 0x434:**
```
@0x43C: IFUW addr=0x0020 != 0xa455, else +0x5  ← GM check (skip if NOT at transition)
@0x444: MUSIC
@0x448: IFUW addr=0x0020 != 0xa455, else +0x3  ← Second GM check
@0x450: MUSIC
@0x452: RET
```

**Key insight:**
- These are `!=` checks (not `==`)
- When GM **IS** 0xa455, checks pass through → music plays
- When GM is **NOT** 0xa455, else-skip happens → skip music

**The problem for single-disc:**
CSR multi-disc sets GM=0xa455 during disc swap. Single-disc **never** reaches that GM value because there's no physical disc swap event. So:
- LOST2 loads with GM != 0xa455
- First IFUW: else +0x5 → skips MUSIC at 0x444
- Second IFUW: else +0x3 → skips MUSIC at 0x450
- Hits RET at 0x452 → no music, no further scene logic

**The fix (two options):**
1. **Set GM=0xa455** before LOST2 loads (in LOSIN2 or transition trigger)
2. **Patch both IFUW else offsets to 0x00** in LOST2 → always play music regardless of GM

Option 2 is safer (no risk of breaking other GM-dependent logic).

**Verification (optional):**
You can verify this with Makou Reactor or by decoding the raw bytes:

```bash
cd ~/Final-Fantasy-7-Modding
python3 scripts/decode_field_script.py "1820000055a4000b600e027bff1cfa6500e016"
```

Expected output shows the IFUW at offset 0x00, MAPJUMP at 0x08.

### 3. Find the Actual Bit Flag

Search CSR executable or disc-init code for bank3[0x84] manipulation:

```bash
# In CSR repo if you have SLUS decompressed
strings SLUS_014.46 | grep -i "bank\|0x84"

# Or search in Ghidra (if you have the project)
```

### 4. Apply the Fix (READY TO IMPLEMENT)

Now that we've decoded the exact logic, the fix is straightforward:

**Create v0.1.37 layer:**
- Target: CSR LOST2.DAT relocated to single-disc D1
- Search pattern: `18 20 00 00 55 a4` (start of IFUW at init offset 0x3D)
- Patch offset: +7 bytes from search hit (the "else" parameter)
- Old byte: `0x0b`
- New byte: `0x00`

This will be implemented in `mods/single-disc/scripts/ship_v037.py` using the `build_ic_layer.py` search-and-replace feature.

## Next Steps

**Agent will:**
1. Create `mods/single-disc/scripts/ship_v037.py` with the correct patch
2. Run the script to generate `builder/single-disc-on-csr-v0.1.37/`
3. Update manifest to enable v0.1.37
4. Commit and push

**You will:**
1. Pull the repo
2. Build and test the single-disc with v0.1.37 applied
3. Verify the break scene plays at the D1→D2 transition
4. Verify music plays in LOST2 forest after the break
5. Report back: ✅ or any issues observed

## Context Files

- `docs/reference/disc-transition-knowledge-base.md` - Current findings
- `mods/single-disc/CHANGELOG.md` - History of attempts (v0.1.31-v0.1.36)
- `docs/findings/2026-08-14-break-losin2-bit-and-cos-ask.md` - v0.1.31 gate details

---

**Agent Note:** This task requires human investigation with tools I can't run (Makou Reactor, DuckStation, disc burning). Once you provide the evidence, I can create the exact byte patches needed.
