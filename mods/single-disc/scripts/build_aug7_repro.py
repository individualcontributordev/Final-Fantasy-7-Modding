#!/usr/bin/env python3
"""Rebuild the Aug 6/7-era single-disc playtest bin for regression testing.

Checks out commit 11d6a8d (2026-08-06 22:30, last commit before the Aug 7
ending-credits work started) into a throwaway git worktree, runs *that*
commit's own build_playtest_bin.py against the current pristine discs and
CSR repo, then copies the result back as workspace/iso-extract/aug7-repro.bin
(+.cue). Used to check whether current bugs (Disc 1->2 black screen, Makou
"Invalid archive") already existed before the FIELD.BIN table fix and
ending-credits work.

Usage (from repo root):
    python3 mods/single-disc/scripts/build_aug7_repro.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PINNED_COMMIT = "11d6a8d"
CSR_REPO = REPO_ROOT.parent / "Final-Fantasy-7-CSR"
# build_playtest_bin.py looks for the CSR repo as a sibling of its own repo
# root, so the worktree must live next to CSR_REPO too (no symlink needed).
WORKTREE = CSR_REPO.parent / ".ff7-aug7-build-tmp"
BUILT_BIN = "ff7_d1_playtest_csr_sd_movies.bin"
BUILT_CUE = "ff7_d1_playtest_csr_sd_movies.cue"
OUT_BIN = REPO_ROOT / "workspace/iso-extract/aug7-repro.bin"
OUT_CUE = REPO_ROOT / "workspace/iso-extract/aug7-repro.cue"


def run(cmd, **kwargs):
    print(f"+ {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, check=True, **kwargs)


def link_or_copy(src: Path, dst: Path):
    """Hardlink src at dst if possible (same volume, no privilege needed on
    Windows), else fall back to a full copy. Avoids os.symlink, which needs
    admin rights / Developer Mode on Windows."""
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    try:
        import os

        os.link(src, dst)
    except OSError:
        shutil.copyfile(src, dst)


def main():
    if not CSR_REPO.exists():
        sys.exit(f"FAIL: CSR repo not found at {CSR_REPO}")

    pristine_dir = REPO_ROOT / "workspace/pristine"
    pristine_bins = sorted(pristine_dir.glob("*.bin"))
    if not pristine_bins:
        sys.exit(f"FAIL: no pristine *.bin files in {pristine_dir}")

    # Clean any stale worktree from a previous failed run.
    if WORKTREE.exists():
        run(["git", "worktree", "remove", str(WORKTREE), "--force"], cwd=REPO_ROOT)

    run(["git", "worktree", "add", str(WORKTREE), PINNED_COMMIT], cwd=REPO_ROOT)

    worktree_pristine = WORKTREE / "workspace/pristine"
    worktree_pristine.mkdir(parents=True, exist_ok=True)
    for f in pristine_bins:
        link_or_copy(f, worktree_pristine / f.name)

    try:
        run(
            [sys.executable, "mods/single-disc/scripts/build_playtest_bin.py"],
            cwd=WORKTREE,
        )

        built_bin = WORKTREE / "workspace/iso-extract" / BUILT_BIN
        built_cue = WORKTREE / "workspace/iso-extract" / BUILT_CUE
        if not built_bin.exists():
            sys.exit(f"FAIL: expected build output missing: {built_bin}")

        OUT_BIN.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(built_bin, OUT_BIN)
        cue_text = built_cue.read_text(encoding="utf-8").replace(BUILT_BIN, OUT_BIN.name)
        OUT_CUE.write_text(cue_text, encoding="utf-8")

        print(f"WROTE {OUT_BIN} ({OUT_BIN.stat().st_size:,} bytes)")
        print(f"WROTE {OUT_CUE}")
    finally:
        run(["git", "worktree", "remove", str(WORKTREE), "--force"], cwd=REPO_ROOT)


if __name__ == "__main__":
    main()
