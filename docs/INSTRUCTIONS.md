# INSTRUCTIONS — Set up automated Ghidra analysis (Windows + Git Bash)

## What this is

Setting up ghidra-cli so Agent can write automated scripts that:
1. Import game files into Ghidra
2. Run analysis automatically
3. Extract structured metadata (functions, symbols, control flow)
4. Output to JSON that Agent can read

You'll run one command instead of 6 manual export steps. Agent gets exact game structure data for faster modding.

## Your task: Install ghidra-cli (one-time setup)

**Using pre-built Windows binary** (no Rust/compilation needed):

**Prerequisites:**
- Ghidra 10.0+ installed on Windows
- Java 17+ (check: `java --version` in Git Bash)

**Steps:**

1. **Download pre-built Windows binary:**

```bash
# In Git Bash on your Windows Ghidra machine:
cd ~/
mkdir -p ghidra-cli
cd ghidra-cli

# Download latest release (v0.2.1 as of now):
curl -L -o ghidra-cli.zip https://github.com/akiselev/ghidra-cli/releases/download/v0.2.1/ghidra-cli-v0.2.1-x86_64-pc-windows-msvc.zip

# Extract:
unzip ghidra-cli.zip
# Should create ghidra.exe
```

2. **Add to PATH:**

```bash
# Add ghidra-cli directory to PATH in ~/.bashrc:
echo 'export PATH="$HOME/ghidra-cli:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify it's in PATH:
which ghidra
# Should print: /c/Users/YourName/ghidra-cli/ghidra
```

3. **Set GHIDRA_INSTALL_DIR environment variable:**

```bash
# Find your Ghidra install directory (folder with ghidraRun.bat)
# Example: C:/ghidra_11.3_PUBLIC or D:/ghidra_11.3_PUBLIC

# In Git Bash:
# First, find where Ghidra is installed on your system
# It's the directory containing ghidraRun.bat

# Then add to ~/.bashrc (replace with your actual Ghidra path):
echo 'export GHIDRA_INSTALL_DIR="/d/your-ghidra-path-here"' >> ~/.bashrc
source ~/.bashrc

# Verify it's set:
echo $GHIDRA_INSTALL_DIR
# Should print your Ghidra path
```

4. **Test it works:**

```bash
ghidra doctor
# Should show:
#   ✓ Ghidra installation found
#   ✓ analyzeHeadless executable found
#   ✓ Java runtime found
# (or similar success messages)
```

**Paste here:**
1. What's your Ghidra install directory? (the folder with ghidraRun.bat)
2. The full output of `ghidra doctor` after setting GHIDRA_INSTALL_DIR

---

## After successful installation

Agent will write automated Ghidra scripts that you run with simple commands like:

```bash
cd ~/Final-Fantasy-7-Modding
python scripts/ghidra/analyze_field_bin.py
```

This will:
- Import FIELD.BIN into Ghidra automatically
- Run analysis
- Extract functions, symbols, control flow to JSON
- Output to `workspace/ghidra-analysis/field-functions.json`
- You commit the JSON (no raw game code)
- Agent can query it in future sessions!

## Why this matters

**Before (manual):**
- You: manually export from Ghidra (6+ steps)
- Agent: pattern-matches blind, guesses addresses
- Slow, error-prone

**After (automated):**
- You: run one command Agent writes
- Agent: reads exact structure from JSON
- Fast, accurate patches
