# INSTRUCTIONS — Investigate Single-Disc Layer Corruption

## Problem

You reported: "the current single-disc mod when used with the csr layers is broken"

## What I Found

**CRITICAL BUG:** The single-disc layer files are EMPTY!

```bash
cd ~/Final-Fantasy-7-Modding

# Check layer sizes
wc -l builder/single-disc-on-csr-v0.1.33/layers/disc1.layer.json
wc -l builder/single-disc-on-csr-v0.1.35/layers/disc1.layer.json
wc -l builder/single-disc-csr-manip-movies-v0.1.4/layers/disc1.layer.json
```

All three show just 4 lines (empty operations array):
```
{
  "version": "ic-layer-v1",
  "operations": []
}
```

**This is why single-disc breaks CSR - the layers have no patches!**

---

## Root Cause

From CHANGELOG line 42:
> "Core layer bytes still shared from builder/single-disc-on-csr-v0.1.24/."

But v0.1.24 was deleted during the v0.1.33 repo purge (CHANGELOG line 23).

**The actual layer content is missing from the repo.**

---

## Step 1: Check ship scripts

```bash
cd ~/Final-Fantasy-7-Modding
ls -la mods/single-disc/scripts/ship_*.py
```

Paste the output. We need to find the latest ship script to rebuild the layers.

---

## Step 2: Also paste this info

1. **Which CSR version are you using?**
   ```bash
   # If you have a built image, check APPLIED.txt
   cat path/to/APPLIED.txt | grep csr
   ```

2. **What breaks specifically?**
   - Wrong field behavior?
   - Crashes?
   - Wrong movies?
   - Disc-ask prompts reappear?

3. **Where does it break?**
   - Immediately on boot?
   - At specific story point (e.g., LOSIN2 → LOST2)?

---

## Why This Matters

The empty layers mean:
- ❌ No Ask-for-disc removal
- ❌ No SNOVA LBA patches  
- ❌ No field movie handling
- ❌ No disc-break choreography

Basically the "single-disc" mod does **nothing** when applied, so CSR multi-disc behavior is intact and breaks on a single disc image.

---

## Next Steps

Once you paste the ship script list and problem details, I'll:
1. Run/write the build script to regenerate layers
2. Commit the rebuilt layers with proper content
3. Fix the manifest references
4. Verify against CSR
