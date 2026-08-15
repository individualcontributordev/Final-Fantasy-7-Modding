# INSTRUCTIONS — Debug Ghidra Headless Extraction

## Goal

Get Ghidra's `analyzeHeadless` working so we can batch-extract metadata from all game binaries automatically.

## Prerequisites

- Ghidra installed and working in GUI
- FF7 project with FIELD.BIN.dec already imported and analyzed
- Git Bash or similar terminal

---

## Step 1: Find analyzeHeadless.bat

First, locate your Ghidra installation's `analyzeHeadless.bat`:

```bash
cd ~/Final-Fantasy-7-Modding
ls -la "D:/tools/ghidra_12.1_PUBLIC/support/analyzeHeadless.bat"
```

If that path doesn't exist, find it:

```bash
# Common locations on Windows:
ls -la /c/ghidra*/support/analyzeHeadless.bat
ls -la /d/tools/ghidra*/support/analyzeHeadless.bat
ls -la "$PROGRAMFILES/ghidra"*/support/analyzeHeadless.bat
```

**Paste the path you find.**

---

## Step 2: Test analyzeHeadless directly

Once you have the path, test it with a simple command:

```bash
cd ~/Final-Fantasy-7-Modding

# Replace D:/tools/ghidra_12.1_PUBLIC with YOUR actual Ghidra path
"D:/tools/ghidra_12.1_PUBLIC/support/analyzeHeadless.bat" --help
```

**What happens?**
- ✅ Shows help text → Good!
- ❌ Hangs → Ghidra installation issue
- ❌ "command not found" → Wrong path

**Paste the output.**

---

## Step 3: List programs in your FF7 project

```bash
cd ~/Final-Fantasy-7-Modding

# Replace with your actual Ghidra path and project location
"D:/tools/ghidra_12.1_PUBLIC/support/analyzeHeadless.bat" \
  "D:/your-ghidra-projects-dir/" \
  FF7 \
  -process / \
  -noanalysis
```

**Expected:** Should list "FIELD.BIN.dec" and exit.

**Paste what happens:**
- Does it print the program name?
- Does it hang?
- Any errors?

---

## Step 4: Run extraction script on FIELD.BIN.dec

If Step 3 worked, try running the extraction script:

```bash
cd ~/Final-Fantasy-7-Modding

# Replace paths as needed
"D:/tools/ghidra_12.1_PUBLIC/support/analyzeHeadless.bat" \
  "D:/your-ghidra-projects-dir/" \
  FF7 \
  -process FIELD.BIN.dec \
  -postScript "D:/projects/Final-Fantasy-7-Modding/scripts/ghidra/ExtractFieldMetadata.java" \
  -noanalysis
```

**Expected:** Should run the script and create JSON files.

**What happens:**
- Does it complete?
- Does it hang? (If so, **Ctrl+C after 30 seconds** and paste output)
- Any errors?

**Paste the full output.**

---

## Step 5: Paste evidence and we'll fix it

Once you've run Steps 1-4 and pasted the output, Agent will:
1. Identify exactly why it's hanging
2. Fix the script or workflow
3. Get batch extraction working

Then we can extract all 10+ game files automatically!



