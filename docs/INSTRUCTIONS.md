# INSTRUCTIONS — Extract Metadata from All Game Binaries

## Goal

Extract functions and symbols from all FF7 game binaries in your Ghidra project as JSON files.

## What You Already Have ✅

Based on your Ghidra project logs, these files are already imported and analyzed:
- **FIELD.BIN.dec** (186 functions) ✅ metadata extracted
- **BATTLE.X.dec** (615 functions) ← extract this next
- **BATRES.X.dec** (18 functions)
- **WORLD.BIN.dec** (446 functions)
- **SCUS_941.63** (1145 functions)

**Total: 5 files, ~2410 functions ready to extract!**

---

## Step 1: Extract metadata in Ghidra GUI

Since you already have all the files imported, just run the extraction script on each one:

**For each file:**

1. Open Ghidra GUI
2. Open your `FF7` project  
3. Double-click the file (e.g., `BATTLE.X.dec`)
4. Open Script Manager: **Window → Script Manager** (`Ctrl+Shift+S`)
5. Browse to: `D:/projects/Final-Fantasy-7-Modding/scripts/ghidra/`
6. Double-click `ExtractFieldMetadata.java` to run it
7. Wait 10-30 seconds
8. Check Console for "Extraction complete!"

**Files to extract (in order of importance):**
1. ✅ FIELD.BIN.dec (already done - 26 KB JSON)
2. **BATTLE.X.dec** (battle engine - important for single-disc)
3. **BATRES.X.dec** (victory fanfare)
4. **WORLD.BIN.dec** (world map - may have disc checks)
5. SCUS_941.63 (main executable - optional)

---

## Step 2: Collect all the JSON files

After running on all files, you should have:

```bash
cd ~/Final-Fantasy-7-Modding
ls -lh scripts/ghidra/*.json

# Expected output:
# field-functions.json (26 KB) ✅
# field-symbols.json (4 B) ✅
# battle-functions.json (new)
# battle-symbols.json (new)
# batres-functions.json (new)
# batres-symbols.json (new)
# world-functions.json (new)
# world-symbols.json (new)
# scus-functions.json (new)
# scus-symbols.json (new)
```

---

## Step 3: Copy to workspace

```bash
cd ~/Final-Fantasy-7-Modding
mkdir -p workspace/ghidra-analysis

# Copy all JSON files
cp scripts/ghidra/*-functions.json workspace/ghidra-analysis/
cp scripts/ghidra/*-symbols.json workspace/ghidra-analysis/

# Verify
ls -lh workspace/ghidra-analysis/
```

---

## Step 4: Commit the metadata

```bash
cd ~/Final-Fantasy-7-Modding
git add workspace/ghidra-analysis/
git commit -m "Add Ghidra metadata for all game binaries

Extracted functions and symbols from:
- FIELD.BIN.dec (186 functions)
- BATTLE.X.dec (615 functions)
- BATRES.X.dec (18 functions)
- WORLD.BIN.dec (446 functions)
- SCUS_941.63 (1145 functions)

Total: ~2410 functions across 5 core modules.
Agent can now query complete game structure."
git push
```

---

## Step 5: Paste evidence

Once committed, paste:

```bash
git log -1 --stat
ls -lh workspace/ghidra-analysis/
```

✅ **Done!** Agent now has complete metadata for the entire FF7 PSX engine.

---

## Why This Matters

With metadata for all these files, Agent can:
- Find all disc-related code across all modules
- Map cross-module calls (FIELD→BATTLE, BATRES→BATTLE, etc.)
- Identify hardcoded addresses for patching
- Plan new features (button combos, debug menus, etc.)
- Verify no disc checks remain in single-disc mod

**Files extracted = complete game logic database!**
