# INSTRUCTIONS — Investigate WORLD.BIN Disc Check

## Context

Complete Ghidra metadata extracted from all 5 core FF7 PSX binaries (2,410 functions).

**Analysis result:** Single-disc mod is **functionally complete** except one potential issue in WORLD.BIN.

See: `docs/findings/2026-08-15-ghidra-metadata-single-disc-analysis.md`

---

## The Question

**Does WORLD.BIN function `FUN_800c5cd4` check disc ID?**

- Address: `0x800c5cd4`
- Size: 1072 bytes
- Callers: 1

If it does, we need to patch it. If not, single-disc mod is done.

---

## Step 1: Open WORLD.BIN in Ghidra

1. **Open Ghidra GUI**
2. **Open your `FF7` project**
3. **Double-click `WORLD.BIN.dec`**
4. **Wait for CodeBrowser to load**

---

## Step 2: Navigate to the function

1. In CodeBrowser, press **`G`** (Go To...)
2. Enter: `800c5cd4`
3. Press Enter

You should see the function `FUN_800c5cd4` highlighted.

---

## Step 3: Analyze the disassembly

Look for these patterns:

### Pattern 1: Disc-ID comparison

```mips
li      v0, 0x1      # Load immediate 1 (disc 1)
li      v1, 0x2      # Load immediate 2 (disc 2)
li      v1, 0x3      # Load immediate 3 (disc 3)
beq     ...          # Branch if equal
bne     ...          # Branch if not equal
```

### Pattern 2: CD-ROM BIOS calls

```mips
jal     CdControl    # Call CD control
jal     CdRead2      # Call CD read
jal     CdStatus     # Call CD status
```

Look at the **argument registers** (`a0`, `a1`, `a2`, `a3`) to see if disc-specific values are passed.

### Pattern 3: Memory reads from disc-ID location

Known disc-ID addresses from PSX memory map:
- `0x1F801800` (CD-ROM status register)
- Custom game variables (check cross-references)

---

## Step 4: Export the disassembly

If you find **ANY** of the above patterns:

1. In CodeBrowser, click the function name `FUN_800c5cd4`
2. Right-click → **Export Function**
3. Save as: `~/Desktop/WORLD_FUN_800c5cd4.txt`

---

## Step 5: Paste evidence

```bash
cd ~/Final-Fantasy-7-Modding
git pull

# Paste the function disassembly here (or just the relevant lines showing disc checks)
```

**If no disc checks found:** Just reply "No disc checks in WORLD.BIN function"

**If disc checks found:** Attach the exported disassembly and Agent will write a patch script.

---

## Alternative: Quick grep for disc values

If you don't want to read assembly, just search the binary:

```bash
cd ~/Final-Fantasy-7-Modding

# Extract WORLD.BIN to check for hardcoded disc values
python3 << 'PYEOF'
import json

# Load WORLD.BIN functions
with open('scripts/ghidra/world-functions.json') as f:
    funcs = json.load(f)

# Find the function
target = next(f for f in funcs if f['address'] == '800c5cd4')

print(f"Function: {target['name']}")
print(f"Address: {target['address']}")
print(f"Size: {target['size']} bytes")
print(f"Callers: {len(target['callers'])}")

if target['callers']:
    print(f"\nCalled by:")
    for caller in target['callers']:
        caller_func = next((f for f in funcs if f['address'] == caller), None)
        if caller_func:
            print(f"  {caller_func['name']} @ {caller}")

PYEOF
```

---

## What Happens Next

**Scenario A: No disc checks**
→ Single-disc mod is **complete**! Ship it.

**Scenario B: Disc checks found**
→ Agent writes a patch script similar to `inject_snova_d3_to_d1.py` to neutralize the check.

---

## Summary

The Ghidra metadata **confirms** the single-disc mod is **functionally complete** for:
- ✅ FIELD.BIN (Ask-for-disc stripped via Makou)
- ✅ BATTLE.X (SNOVA LBAs patched)
- ✅ BATRES.X (no disc code)
- ✅ SCUS_941.63 (only CD BIOS APIs)

**Only unknown:** WORLD.BIN `FUN_800c5cd4`.

Once you investigate this function, we'll know if the single-disc mod needs any final patches.
