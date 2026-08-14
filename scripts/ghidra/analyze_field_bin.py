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
PROJECT_NAME = "ff7-field-analysis"
BASE_ADDRESS = "0x800A0000"  # US FIELD.BIN module base address


def check_prerequisites():
    """Verify all required files and tools exist."""
    print("Checking prerequisites...")
    
    if not FIELD_BIN_DEC.exists():
        print(f"❌ FIELD.BIN.dec not found at: {FIELD_BIN_DEC}")
        print("\nRun this first:")
        print("  python scripts/decompress_gzipps.py \\")
        print("    workspace/iso-extract/FIELD.BIN \\")
        print("    workspace/iso-extract/FIELD.BIN.dec")
        return False
    
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
    except FileNotFoundError:
        print("❌ ghidra command not found. Is ghidra-cli installed and in PATH?")
        return False
    
    print(f"✅ FIELD.BIN.dec found ({FIELD_BIN_DEC.stat().st_size:,} bytes)")
    print(f"✅ ghidra-cli available")
    return True


def run_ghidra_script(script_content: str, output_file: Path) -> bool:
    """Run a Ghidra Python script via ghidra-cli."""
    print(f"\nRunning Ghidra script → {output_file.name}...")

    # Write script to temporary file
    script_file = OUTPUT_DIR / "_temp_script.py"
    script_file.write_text(script_content)

    try:
        # Import and analyze in one step
        # ghidra-cli auto-detects format, but for raw binaries you may need to:
        # 1. Import once through Ghidra GUI with correct settings
        # 2. Then use ghidra-cli to run scripts
        print("  Importing and analyzing FIELD.BIN.dec...")
        print("  (This may take 1-2 minutes on first run)")

        import_cmd = [
            "ghidra",
            "import",
            str(FIELD_BIN_DEC.absolute()),
            "--project", PROJECT_NAME,
            # Don't skip analysis - we need it for extracting functions
        ]

        result = subprocess.run(
            import_cmd,
            capture_output=True,
            text=True,
            cwd=OUTPUT_DIR,
            check=False
        )

        # Check for success or "already exists"
        success = result.returncode == 0
        already_exists = "already exists" in result.stderr or "already exists" in result.stdout

        if not success and not already_exists:
            print(f"❌ Import failed:")
            print("STDERR:", result.stderr)
            print("STDOUT:", result.stdout)
            print("\n⚠️  Note: For raw binaries like FIELD.BIN.dec, you may need to:")
            print("  1. Import it once manually through Ghidra GUI")
            print("  2. Set processor to MIPS:LE:32:default")
            print("  3. Set base address to 0x800A0000")
            print("  4. Run analysis")
            print("  5. Then this script can extract the data")
            return False

        if already_exists:
            print("  ✅ Already imported (using existing)")
        else:
            print("  ✅ Import and analysis complete")

        # Now run the extraction script
        print("  Running extraction script...")
        script_cmd = [
            "ghidra",
            "script", "run",
            str(script_file.absolute()),
            "--project", PROJECT_NAME,
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
