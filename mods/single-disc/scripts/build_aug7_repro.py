#!/usr/bin/env python3
"""Rebuild a historical single-disc playtest bin for regression bisection.

Checks out a given commit (default 11d6a8d, 2026-08-06 22:30, last commit
before the Aug 7 ending-credits work started) into a throwaway git worktree,
runs *that* commit's own build_playtest_bin.py against the current pristine
discs and CSR repo, then copies the result back as
workspace/iso-extract/<commit>-repro.bin (+.cue). Used to bisect when
regressions (Disc 1->2 black screen, Makou "Invalid archive") were
introduced.

Usage (from repo root):
    python3 mods/single-disc/scripts/build_aug7_repro.py [commit]
"""
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
SWAP_ORDER = "--swap-order" in sys.argv[1:]
PINNED_COMMIT = ARGS[0] if ARGS else "11d6a8d"
CSR_REPO = REPO_ROOT.parent / "Final-Fantasy-7-CSR"
# build_playtest_bin.py looks for the CSR repo as a sibling of its own repo
# root, so the worktree must live next to CSR_REPO too (no symlink needed).
WORKTREE = CSR_REPO.parent / ".ff7-aug7-build-tmp"
BUILT_BIN = "ff7_d1_playtest_csr_sd_movies.bin"
BUILT_CUE = "ff7_d1_playtest_csr_sd_movies.cue"
OUT_STEM = f"{PINNED_COMMIT}-repro" + ("-swapped" if SWAP_ORDER else "")
OUT_BIN = REPO_ROOT / f"workspace/iso-extract/{OUT_STEM}.bin"
OUT_CUE = REPO_ROOT / f"workspace/iso-extract/{OUT_STEM}.cue"


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


def repoint_stale_layer_paths(worktree: Path):
    """build_playtest_bin.py hardcodes core/movie layer dirs by version
    (e.g. single-disc-on-csr-v0.1.2). Older retired versions get purged from
    builder/ over time, so for commits where that pinned version no longer
    exists, repoint at the newest single-disc-on-csr-v* / manip-movies-v*
    layer dir actually present in that commit's builder/ tree."""
    import re

    script = worktree / "mods/single-disc/scripts/build_playtest_bin.py"
    text = script.read_text(encoding="utf-8")
    builder_dir = worktree / "builder"

    def latest(prefix: str):
        candidates = sorted(
            (d for d in builder_dir.glob(f"{prefix}-v*") if (d / "layers/disc1.layer.json").is_file()),
            key=lambda d: [int(x) for x in re.findall(r"\d+", d.name.rsplit("-v", 1)[-1])],
        )
        return candidates[-1].name if candidates else None

    core_match = re.search(r'core_layer = ROOT / "builder/(single-disc-on-csr-v[\d.]+)/layers/disc1\.layer\.json"', text)
    movie_match = re.search(r'movie_layer = ROOT / "builder/(single-disc-csr-manip-movies-v[\d.]+)/layers/disc1\.layer\.json"', text)
    core_pinned = core_match.group(1) if core_match else None
    movie_pinned = movie_match.group(1) if movie_match else None
    core_dir = core_pinned
    movie_dir = movie_pinned
    # Only repoint if the commit's own hardcoded version was purged from
    # builder/ (retired). If it's still present, use it as-is so we don't
    # pair a commit's core layer with a *newer* movies layer than it was
    # actually written/tested against.
    if core_pinned and not (builder_dir / core_pinned / "layers/disc1.layer.json").is_file():
        core_dir = latest("single-disc-on-csr")
        text = re.sub(
            r'core_layer = ROOT / "builder/single-disc-on-csr-v[\d.]+/layers/disc1\.layer\.json"',
            f'core_layer = ROOT / "builder/{core_dir}/layers/disc1.layer.json"',
            text,
        )
    if movie_pinned and not (builder_dir / movie_pinned / "layers/disc1.layer.json").is_file():
        movie_dir = latest("single-disc-csr-manip-movies")
        text = re.sub(
            r'movie_layer = ROOT / "builder/single-disc-csr-manip-movies-v[\d.]+/layers/disc1\.layer\.json"',
            f'movie_layer = ROOT / "builder/{movie_dir}/layers/disc1.layer.json"',
            text,
        )
    script.write_text(text, encoding="utf-8")
    print(f"layers -> core={core_dir} (pinned={core_pinned}), movies={movie_dir} (pinned={movie_pinned})")


def swap_apply_order(worktree: Path):
    """DIAGNOSTIC ONLY: swap this commit's build_playtest_bin.py so
    manip-movies is applied BEFORE the single-disc main pack (matching the
    production builder's addonApplyRank fix: movies=10, single-disc-on-csr=20,
    introduced in 6ba3f34's finding docs/findings/2026-08-13-path-fmv-movies-pack-clobber.md).
    This dev script never got that reordering, so it may be reproducing a
    bug that's already fixed in the real builder pipeline."""
    script = worktree / "mods/single-disc/scripts/build_playtest_bin.py"
    text = script.read_text(encoding="utf-8")
    old = (
        '    print("2/3 single-disc main pack...")\n'
        '    apply_layer(img, json.loads(core_layer.read_text(encoding="utf-8")))\n'
        '    print("   ", len(img), "bytes")\n'
        '    j_core = extract_file(bytes(img), "MOVIE/JAIROFAL.MOV")\n'
        '    van = extract_file(pristine.read_bytes(), "MOVIE/JAIROFAL.MOV")\n'
        '    print("   JAIROFAL after main size", len(j_core), "(still D1-family until movies)")\n'
        '\n'
        '    print("3/3 manip-movies v0.1.2 cumulative (seed + LBA 250450)...")\n'
        '    apply_layer(img, json.loads(movie_layer.read_text(encoding="utf-8")))\n'
        '    print("   ", len(img), "bytes")\n'
    )
    new = (
        '    print("2/3 manip-movies v0.1.2 cumulative (seed + LBA 250450) [SWAPPED FIRST]...")\n'
        '    apply_layer(img, json.loads(movie_layer.read_text(encoding="utf-8")))\n'
        '    print("   ", len(img), "bytes")\n'
        '\n'
        '    print("3/3 single-disc main pack [SWAPPED SECOND]...")\n'
        '    apply_layer(img, json.loads(core_layer.read_text(encoding="utf-8")))\n'
        '    print("   ", len(img), "bytes")\n'
        '    j_core = extract_file(bytes(img), "MOVIE/JAIROFAL.MOV")\n'
        '    van = extract_file(pristine.read_bytes(), "MOVIE/JAIROFAL.MOV")\n'
        '    print("   JAIROFAL after main size", len(j_core), "(still D1-family until movies)")\n'
    )
    if old not in text:
        sys.exit("FAIL: --swap-order could not find expected apply-order block to patch")
    script.write_text(text.replace(old, new), encoding="utf-8")
    print("SWAPPED apply order -> movies then single-disc main pack")


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

    repoint_stale_layer_paths(WORKTREE)
    if SWAP_ORDER:
        swap_apply_order(WORKTREE)

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
