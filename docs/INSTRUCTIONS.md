# INSTRUCTIONS — Export FIELD.BIN from Ghidra for Agent analysis

## What this is

Creating a proof-of-concept workflow where:
1. You export decompiled FIELD.BIN from Ghidra (stays local, gitignored)
2. You run a parser script that extracts structured metadata
3. You commit the structured output (no raw game code)
4. Agent can read the metadata in future sessions for faster modding

This will make field script patching much faster - Agent can query function addresses, control flow, and symbols instead of blind pattern-matching.

## Your task: Export FIELD.BIN from Ghidra (one-time setup)

**Prerequisites:**
- Ghidra installed
- FIELD.BIN already decompressed

**Steps:**

1. **Decompress FIELD.BIN if you haven't already:**

```bash
cd ~/Final-Fantasy-7-Modding
python scripts/decompress_gzipps.py \
  workspace/iso-extract/FIELD.BIN \
  workspace/iso-extract/FIELD.BIN.dec
```

2. **Import FIELD.BIN into Ghidra:**
   - Open Ghidra → New Project (or use existing)
   - File → Import File → Browse to `workspace/iso-extract/FIELD.BIN.dec`
   - Format: **Raw Binary**
   - Language: **MIPS:LE:32:default**
   - Base address: **`0x800A0000`** (US FIELD.BIN module base)
   - Click OK

3. **Let Ghidra analyze:**
   - Click "Yes" when prompted to analyze
   - Wait for auto-analysis to complete (may take 5-10 minutes)
   - Check status in bottom-right corner

4. **Export the full listing:**
   - File → Export Program
   - Format: Choose the best text-based option (HTML, Text, or C/C++)
   - Output file: `workspace/ghidra-exports/FIELD.BIN.listing.txt`
     (create the `ghidra-exports` directory if it doesn't exist)
   - Include: Everything (full program)
   - Click OK
   - **Note:** This file will be large and is gitignored - stays local only

5. **Export functions list:**
   - Window → Functions (or press Ctrl+F to open Functions window)
   - Select All (Ctrl+A)
   - Right-click → Export → CSV
   - Save as: `workspace/ghidra-exports/FIELD.BIN.functions.csv`

6. **Export symbol table:**
   - Window → Symbol Table
   - Right-click in the table → Export → CSV
   - Save as: `workspace/ghidra-exports/FIELD.BIN.symbols.csv`

7. **Verify exports exist:**

```bash
cd ~/Final-Fantasy-7-Modding
mkdir -p workspace/ghidra-exports
ls -lh workspace/ghidra-exports/
# Should show:
#   FIELD.BIN.listing.txt (large file)
#   FIELD.BIN.functions.csv
#   FIELD.BIN.symbols.csv
```

8. **Paste here the first 30 lines** of `FIELD.BIN.listing.txt` so Agent can see the format and update the parser script.

## After you paste the sample

Agent will:
1. Update `scripts/ghidra/parse_field_listing.py` to parse your listing format
2. You'll run: `python scripts/ghidra/parse_field_listing.py`
3. It will output to: `workspace/ghidra-analysis/field-functions.json`
4. You commit and push that JSON file
5. Agent can now query FIELD.BIN structure in future sessions!

## Why this matters

Currently when patching field code, Agent has to:
- Guess where functions are
- Pattern-match blind through bytecode
- Ask you to check addresses in Ghidra

After this workflow:
- Agent reads `field-functions.json` directly
- Knows exact addresses, function sizes, call graphs
- Patches with confidence, not guesswork
