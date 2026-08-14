# INSTRUCTIONS — Set up automated Ghidra analysis (Windows + Git Bash)

## What this is

Setting up a Ghidra CLI tool so Agent can write automated scripts that:
1. Import game files into Ghidra
2. Run analysis automatically
3. Extract structured metadata (functions, symbols, control flow)
4. Output to JSON that Agent can read

You'll run one command instead of 6 manual export steps. Agent gets exact game structure data for faster modding.

## Your task: Install Ghidra CLI tool (one-time setup)

**Choose ONE option below** (I recommend Option A for Windows + Git Bash):

### Option A: ghidra-rpc (Python-based, recommended for Windows)

**Prerequisites:**
- Ghidra 11.0+ installed on Windows
- Python 3.11+ (check: `python --version` in Git Bash)
- Java 17+ (check: `java --version`)

**Steps:**

1. **Install uv (Python package installer):**

```bash
# In Git Bash on your Windows Ghidra machine:
curl -LsSf https://astral.sh/uv/install.sh | sh
# Close and reopen Git Bash after install
```

2. **Set GHIDRA_INSTALL_DIR environment variable:**

```bash
# Find your Ghidra install directory (contains ghidraRun.bat)
# Example: C:/ghidra_11.3_PUBLIC

# Add to ~/.bashrc (create if doesn't exist):
echo 'export GHIDRA_INSTALL_DIR="/c/ghidra_11.3_PUBLIC"' >> ~/.bashrc
source ~/.bashrc

# Verify:
echo $GHIDRA_INSTALL_DIR
# Should print: /c/ghidra_11.3_PUBLIC (or your path)
```

3. **Clone and install ghidra-rpc:**

```bash
cd ~/
git clone https://github.com/cellebrite-labs/ghidra-rpc.git
cd ghidra-rpc
uv tool install .

# Verify:
ghidra-rpc --version
# Should print: ghidra-rpc, version 0.1.0
```

4. **Test it works:**

```bash
ghidra-rpc doctor
# Should show:
#   ✓ Ghidra installation directory
#   ✓ analyzeHeadless
#   ✓ Project directory
```

**Done!** Skip to "After installation" section below.

---

### Option B: ghidra-cli (Rust-based, original tool you linked)

**Prerequisites:**
- Ghidra 10.0+ installed
- Java 17+
- Rust 1.70+ toolchain

**Steps:**

1. **Install Rust (if not already installed):**

```bash
# In Git Bash:
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

2. **Set GHIDRA_INSTALL_DIR:**

```bash
echo 'export GHIDRA_INSTALL_DIR="/c/ghidra_11.3_PUBLIC"' >> ~/.bashrc
source ~/.bashrc
```

3. **Clone and build ghidra-cli:**

```bash
cd ~/
git clone https://github.com/akiselev/ghidra-cli.git
cd ghidra-cli
cargo install --path .

# Verify:
ghidra doctor
```

---

## After installation (either option)

**Paste here which option you chose** and the output of the doctor/version check command.

Agent will then write automation scripts for your chosen CLI tool!

## Why this matters

**Before (manual):**
- You: manually export from Ghidra (6+ steps)
- Agent: pattern-matches blind, guesses addresses
- Slow, error-prone

**After (automated):**
- You: run one command Agent writes
- Agent: reads exact structure from JSON
- Fast, accurate patches
