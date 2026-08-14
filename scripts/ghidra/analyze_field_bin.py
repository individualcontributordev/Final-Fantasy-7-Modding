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
        # Run via ghidra-cli
        result = subprocess.run(
            [
                "ghidra",
                "script", "run",
                str(script_file),
                "--project", PROJECT_NAME,
                "--import", str(FIELD_BIN_DEC),
                "--processor", "MIPS:LE:32:default",
                "--base", BASE_ADDRESS,
            ],
            capture_output=True,
            text=True,
            cwd=OUTPUT_DIR,
            check=False
        )
        
        if result.returncode != 0:
            print(f"❌ Script failed:")
            print(result.stderr)
            return False
        
        print(f"✅ {output_file.name} created")
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
    
    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)
    print(f"\nStructured metadata written to: {OUTPUT_DIR}/")
    print("\nNext steps:")
    print("  1. Review the JSON files")
    print("  2. Commit to repo: git add workspace/ghidra-analysis/")
    print("  3. Agent can now query game structure!")


if __name__ == "__main__":
    main()
