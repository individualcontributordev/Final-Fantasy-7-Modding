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

➜  Final-Fantasy-7-Modding git:(main) which ghidra
/d/ghidra-cli-v0.2.2/ghidra

3. **Set GHIDRA_INSTALL_DIR environment variable:**

```bash
# Find your Ghidra install directory (folder with ghidraRun.bat)
# Example: C:/ghidra_11.3_PUBLIC or D:/ghidra_11.3_PUBLIC

# Manually add this line to your ~/.zshrc file:
#   export GHIDRA_INSTALL_DIR="/d/your-ghidra-path-here"
# (replace with your actual Ghidra installation path)

# After editing ~/.zshrc, reload it:
source ~/.zshrc

# Verify it's set:
echo $GHIDRA_INSTALL_DIR
# Should print your Ghidra path
```

➜  Final-Fantasy-7-Modding git:(main) ✗ echo $GHIDRA_INSTALL_DIR
/d/ghidra-cli-v0.2.2

4. **Test it works:**

```bash
ghidra doctor
# Should show:
#   ✓ Ghidra installation found
#   ✓ analyzeHeadless executable found
#   ✓ Java runtime found
# (or similar success messages)
```

➜  Final-Fantasy-7-Modding git:(main) ✗ ghidra doctor
Ghidra CLI Doctor
=================

Checking Ghidra installation... OK
  Location: D:/ghidra-cli-v0.2.2
  analyzeHeadless: NOT FOUND

Checking Java (full JDK 21+)... OK
  JDK 21 at C:/Users/David/.sdkman/candidates/java/current (selected via JAVA_HOME)

Checking bridge script compiles... FAILED
  No Ghidra jars found to compile against

Checking project directory... OK
  Location: C:\Users\David\AppData\Local\ghidra-cli\projects
  Exists: yes

Config file... OK
  Location: C:\Users\David\AppData\Roaming\ghidra-cli\config.yaml
  Exists: no

Done!

5. **Report back:**

Add a section to this file with:

```markdown
## Setup completed

Ghidra install directory: /d/your-path-here
ghidra-cli location: /d/ghidra-cli-v0.2.2

Output of `ghidra doctor`:
```
[paste output here]
```
```

Then commit and push this file.

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


## Setup Completed ✅

Ghidra install directory: `D:/ghidra_12.1_PUBLIC/ghidra_12.1_PUBLIC`
ghidra-cli location: `/d/ghidra-cli-v0.2.2`

Output of `ghidra doctor`:

```
Ghidra CLI Doctor
=================

Checking Ghidra installation... OK
  Location: D:/ghidra_12.1_PUBLIC/ghidra_12.1_PUBLIC
  analyzeHeadless: OK

Checking Java (full JDK 21+)... OK
  JDK 21 at C:/Users/David/.sdkman/candidates/java/current (selected via JAVA_HOME)

Checking bridge script compiles... OK

Checking project directory... OK
  Location: C:\Users\David\AppData\Local\ghidra-cli\projects
  Exists: yes

Config file... OK
  Location: C:\Users\David\AppData\Roaming\ghidra-cli\config.yaml
  Exists: no

Done!
```

---

## Next: Run Automated Analysis

Now that ghidra-cli is set up, you can run automated Ghidra analysis scripts!

### Step 1: Extract FIELD.BIN from your disc image

First, check if FIELD.BIN already exists:

```bash
cd ~/Final-Fantasy-7-Modding
ls -lh workspace/iso-extract/FIELD.BIN
```

If it doesn't exist, extract it from your disc `.bin` file:

```bash
# Extract FIELD.BIN from disc 1
# (Replace workspace/pristine/FINALFANTASY7_D1.bin with your actual disc path)
python scripts/extract_from_iso.py \
  workspace/pristine/FINALFANTASY7_D1.bin \
  FIELD/FIELD.BIN \
  workspace/iso-extract/FIELD.BIN
```

If you don't know where your disc `.bin` files are, search for them:

```bash
# Common locations:
ls -lh workspace/pristine/*.bin
ls -lh ~/ff7/*.bin
ls -lh /d/*.bin
```

Verify it extracted:

```bash
ls -lh workspace/iso-extract/FIELD.BIN
# Should show a file around 3-4 MB (compressed)
```

### Step 2: Decompress FIELD.BIN

```bash
cd ~/Final-Fantasy-7-Modding
python scripts/decompress_gzipps.py \
  workspace/iso-extract/FIELD.BIN \
  workspace/iso-extract/FIELD.BIN.dec
```

This should create `FIELD.BIN.dec` (around 6-7 MB uncompressed).

### Step 3: Run the analysis script

```bash
python scripts/ghidra/analyze_field_bin.py
```

This will:
1. Import FIELD.BIN.dec into Ghidra
2. Run auto-analysis
3. Extract structured metadata (functions, symbols, xrefs)
4. Output JSON to `workspace/ghidra-analysis/`

### Step 4: Commit the metadata

```bash
git add workspace/ghidra-analysis/
git commit -m "Add Ghidra analysis metadata for FIELD.BIN"
git push
```

Agent can then query the JSON files in future sessions for accurate patching!

See `docs/06-ghidra-automation.md` for full workflow documentation.



➜  Final-Fantasy-7-Modding git:(main) python scripts/ghidra/analyze_field_bin.py
======================================================================
FF7 FIELD.BIN Ghidra Analysis
======================================================================
Checking prerequisites...
✅ FIELD.BIN.dec found (264,008 bytes)
✅ ghidra-cli available

======================================================================
Analysis complete!
======================================================================

Structured metadata written to: D:\projects\Final-Fantasy-7-Modding\workspace\ghidra-analysis/

Next steps:
  1. Review the JSON files
  2. Commit to repo: git add workspace/ghidra-analysis/
  3. Agent can now query game structure!



   Final-Fantasy-7-Modding git:(main) python scripts/ghidra/analyze_field_bin.py
======================================================================
FF7 FIELD.BIN Ghidra Analysis
======================================================================
Checking prerequisites...
✅ FIELD.BIN.dec found (264,008 bytes)
✅ ghidra-cli available

Running Ghidra script → field-functions.json...
  Importing/analyzing FIELD.BIN.dec in Ghidra...
❌ Import/analysis failed:
error: unexpected argument 'D:\projects\Final-Fantasy-7-Modding\workspace\iso-extract\FIELD.BIN.dec' found

Usage: ghidra analyze [OPTIONS]

For more information, try '--help'.



➜  Final-Fantasy-7-Modding git:(main) python scripts/ghidra/analyze_field_bin.py
======================================================================
FF7 FIELD.BIN Ghidra Analysis
======================================================================
Checking prerequisites...
✅ FIELD.BIN.dec found (264,008 bytes)
✅ ghidra-cli available

Running Ghidra script → field-functions.json...
  Importing FIELD.BIN.dec into Ghidra...
❌ Import failed:
Initializing project (importing D:\projects\Final-Fantasy-7-Modding\workspace\iso-extract\FIELD.BIN.dec)...
Error: Ghidra import did not report success