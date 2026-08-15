#!/usr/bin/env python3
"""
Automated batch extraction from all FF7 game binaries using Ghidra headless.

This uses analyzeHeadless directly (not ghidra-cli bridge) to avoid connection issues.

Usage:
    python scripts/ghidra/extract_all_bins.py

Requirements:
    - GHIDRA_INSTALL_DIR environment variable set
    - Game files already imported in Ghidra project
"""

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = REPO_ROOT / "workspace" / "ghidra-analysis"
PROJECT_NAME = "FF7"
SCRIPT_PATH = REPO_ROOT / "scripts" / "ghidra" / "ExtractFieldMetadata.java"

# Files to extract metadata from
PROGRAMS = [
    "FIELD.BIN.dec",
    "BATTLE.BIN.dec",
    "SCENE.BIN.dec",
    "WORLD.BIN.dec",
]

def get_ghidra_headless():
    """Get path to analyzeHeadless executable."""
    ghidra_dir = os.environ.get("GHIDRA_INSTALL_DIR")
    if not ghidra_dir:
        print("❌ GHIDRA_INSTALL_DIR not set")
        print("Set it in your ~/.zshrc or ~/.bashrc:")
        print('  export GHIDRA_INSTALL_DIR="/path/to/ghidra_12.1_PUBLIC"')
        return None
    
    ghidra_path = Path(ghidra_dir)
    
    # Try common locations for analyzeHeadless
    candidates = [
        ghidra_path / "support" / "analyzeHeadless.bat",
        ghidra_path / "support" / "analyzeHeadless",
    ]
    
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    
    print(f"❌ analyzeHeadless not found in {ghidra_path}")
    return None


def run_headless_analysis(program_name: str) -> bool:
    """Run Ghidra headless analysis on a program."""
    headless = get_ghidra_headless()
    if not headless:
        return False
    
    print(f"\n{'='*70}")
    print(f"Extracting metadata from: {program_name}")
    print(f"{'='*70}")
    
    # Build command
    # analyzeHeadless <project_dir> <project_name> -process <program> -postScript <script>
    cmd = [
        headless,
        str(OUTPUT_DIR.parent),  # Project directory (workspace/)
        PROJECT_NAME,             # Project name
        "-process", program_name, # Which program to process
        "-postScript", str(SCRIPT_PATH),  # Script to run after analysis
        "-noanalysis",            # Don't re-analyze (already done in GUI)
    ]
    
    print(f"Running: {' '.join(cmd)}")
    print("")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            print(f"❌ Failed for {program_name}")
            print("STDERR:", result.stderr)
            if result.stdout:
                print("STDOUT:", result.stdout)
            return False
        
        print(f"✅ Extraction complete for {program_name}")
        if result.stdout:
            print(result.stdout)
        return True
        
    except subprocess.TimeoutExpired:
        print(f"❌ Timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Extract metadata from all game binaries."""
    print("FF7 Batch Metadata Extraction")
    print("="*70)
    
    # Check Ghidra is available
    if not get_ghidra_headless():
        sys.exit(1)
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Process each program
    success_count = 0
    for program in PROGRAMS:
        if run_headless_analysis(program):
            success_count += 1
    
    # Summary
    print("\n" + "="*70)
    print(f"Extraction Summary: {success_count}/{len(PROGRAMS)} succeeded")
    print("="*70)
    
    if success_count == len(PROGRAMS):
        print("\n✅ All files extracted successfully!")
        print(f"\nOutput files in: {OUTPUT_DIR}")
        print("\nNext steps:")
        print("  git add workspace/ghidra-analysis/")
        print('  git commit -m "Add Ghidra metadata for all game binaries"')
        print("  git push")
    else:
        print(f"\n⚠️  {len(PROGRAMS) - success_count} files failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
