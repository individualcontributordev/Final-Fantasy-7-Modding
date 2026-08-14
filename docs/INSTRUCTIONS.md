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


➜  Final-Fantasy-7-Modding git:(main) ghidra doctor
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