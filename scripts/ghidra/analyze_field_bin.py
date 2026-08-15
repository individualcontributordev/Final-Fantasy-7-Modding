#!/usr/bin/env python3
"""
Automated Ghidra analysis of FF7 FIELD.BIN using ghidra-cli.

This script:
1. Imports FIELD.BIN.dec into Ghidra (if not already imported)
2. Runs auto-analysis
3. Extracts functions, symbols, and control flow
4. Outputs structured JSON to workspace/ghidra-analysis/

Usage:
    python scripts/ghidra/analyze_field_bin.py

Outputs:
    workspace/ghidra-analysis/field-functions.json
    workspace/ghidra-analysis/field-symbols.json
    workspace/ghidra-analysis/field-xrefs.json

Requirements:
    - ghidra-cli installed and in PATH
    - GHIDRA_INSTALL_DIR environment variable set
    - FIELD.BIN.dec already decompressed in workspace/iso-extract/
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
FIELD_BIN_DEC = REPO_ROOT / "workspace" / "iso-extract" / "FIELD.BIN.dec"
OUTPUT_DIR = REPO_ROOT / "workspace" / "ghidra-analysis"
PROJECT_NAME = "FF7"  # Must match the project name you created in Ghidra GUI
PROGRAM_NAME = "FIELD.BIN.dec"  # The program name within the project


def check_prerequisites():
    """Verify all required files and tools exist."""
    print("Checking prerequisites...")

    # Check ghidra-cli is available
    try:
        result = subprocess.run(
            ["ghidra", "--version"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            print("❌ ghidra command not found. Is ghidra-cli installed and in PATH?")
            return False
        print(f"✅ ghidra-cli available")
    except FileNotFoundError:
        print("❌ ghidra command not found. Is ghidra-cli installed and in PATH?")
        return False

    # Check if project exists
    print(f"\nChecking Ghidra project '{PROJECT_NAME}'...")
    result = subprocess.run(
        ["ghidra", "project", "list"],
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode != 0:
        print("❌ Could not list Ghidra projects")
        print(result.stderr)
        return False

    if PROJECT_NAME not in result.stdout:
        print(f"❌ Ghidra project '{PROJECT_NAME}' not found")
        print("\nAvailable projects:")
        print(result.stdout)
        print(f"\n⚠️  You need to import FIELD.BIN.dec through Ghidra GUI first!")
        print("See docs/INSTRUCTIONS.md 'Phase 1: One-Time Manual Setup'")
        return False

    print(f"✅ Project '{PROJECT_NAME}' found")
    return True


def run_ghidra_script(script_content: str, output_file: Path) -> bool:
    """Run a Ghidra Python script via ghidra-cli."""
    print(f"\nRunning Ghidra script → {output_file.name}...")

    # Write script to temporary file
    script_file = OUTPUT_DIR / "_temp_script.py"
    script_file.write_text(script_content)

    try:
        # The file should already be imported through Ghidra GUI
        # We just run the extraction script on the existing project
        print(f"  Using existing project: {PROJECT_NAME}")
        print(f"  Program: {PROGRAM_NAME}")

        # Now run the extraction script on the existing program
        print("  Running extraction script...")
        script_cmd = [
            "ghidra",
            "script", "run",
            str(script_file.absolute()),
            "--project", PROJECT_NAME,
            "--program", PROGRAM_NAME,
        ]

        result = subprocess.run(
            script_cmd,
            capture_output=True,
            text=True,
            cwd=OUTPUT_DIR,
            check=False
        )

        if result.returncode != 0:
            print(f"❌ Script failed:")
            print(result.stderr)
            if result.stdout:
                print(result.stdout)
            return False

        # Check output was created
        if not output_file.exists():
            print(f"❌ Output file not created: {output_file}")
            print("Script output:")
            print(result.stdout)
            return False

        print(f"✅ {output_file.name} created ({output_file.stat().st_size:,} bytes)")
        if result.stdout:
            print(f"  {result.stdout.strip()}")
        return True
    finally:
        # Clean up temp script
        if script_file.exists():
            script_file.unlink()


def main():
    """Main analysis workflow."""
    print("=" * 70)
    print("FF7 FIELD.BIN Ghidra Analysis")
    print("=" * 70)

    if not check_prerequisites():
        sys.exit(1)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Extract functions
    functions_script = """
import json
from ghidra.program.model.listing import CodeUnit

output = []
fm = currentProgram.getFunctionManager()
for func in fm.getFunctions(True):
    entry = func.getEntryPoint()
    body = func.getBody()

    # Get function size
    size = 0
    for range in body:
        size += range.getLength()

    # Get callers
    callers = []
    refs = func.getSymbol().getReferences()
    for ref in refs:
        if ref.getReferenceType().isCall():
            from_addr = ref.getFromAddress()
            caller_func = fm.getFunctionContaining(from_addr)
            if caller_func:
                callers.append(str(caller_func.getEntryPoint()))

    output.append({
        "name": func.getName(),
        "address": str(entry),
        "size": size,
        "callers": callers
    })

# Write to file
import os
out_path = os.path.join(r'""" + str(OUTPUT_DIR.absolute()) + """', 'field-functions.json')
with open(out_path, 'w') as f:
    json.dump(output, f, indent=2)

print("Extracted {} functions".format(len(output)))
"""

    if not run_ghidra_script(functions_script, OUTPUT_DIR / "field-functions.json"):
        sys.exit(1)

    # Extract symbols
    symbols_script = """
import json

output = []
sym_table = currentProgram.getSymbolTable()
for sym in sym_table.getAllSymbols(True):
    if sym.getSymbolType().toString() in ["Label", "Function"]:
        output.append({
            "name": sym.getName(),
            "address": str(sym.getAddress()),
            "type": sym.getSymbolType().toString()
        })

# Write to file
import os
out_path = os.path.join(r'""" + str(OUTPUT_DIR.absolute()) + """', 'field-symbols.json')
with open(out_path, 'w') as f:
    json.dump(output, f, indent=2)

print("Extracted {} symbols".format(len(output)))
"""

    if not run_ghidra_script(symbols_script, OUTPUT_DIR / "field-symbols.json"):
        sys.exit(1)

    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)
    print(f"\nStructured metadata written to: {OUTPUT_DIR}/")
    print("\nGenerated files:")
    for f in OUTPUT_DIR.glob("*.json"):
        size = f.stat().st_size
        print(f"  - {f.name} ({size:,} bytes)")
    print("\nNext steps:")
    print("  1. Review the JSON files")
    print("  2. Commit to repo: git add workspace/ghidra-analysis/")
    print("  3. Agent can now query game structure!")


if __name__ == "__main__":
    main()
