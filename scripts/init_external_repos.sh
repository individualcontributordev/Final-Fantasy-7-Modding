#!/usr/bin/env bash
# Clones (or updates) the RE reference repos used as RAG ground-truth sources.
# Run this once per machine (Mac, WSL workstation, etc.) from the repo root:
#
#   bash scripts/init_external_repos.sh
#
# Repos land in ./external/<name> (gitignored — never committed, re-clone
# locally on each machine instead). Paths are always relative to the repo
# root, so the RAG index built from these sources works identically
# regardless of which machine cloned them.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXTERNAL_DIR="$REPO_ROOT/external"
mkdir -p "$EXTERNAL_DIR"

clone_or_update() {
    local url="$1"
    local dir="$2"
    if [ -d "$dir/.git" ]; then
        echo "==> Updating $(basename "$dir")..."
        git -C "$dir" pull --ff-only
    else
        echo "==> Cloning $(basename "$dir")..."
        git clone --depth 1 "$url" "$dir"
    fi
}

clone_or_update "https://github.com/myst6re/makoureactor.git" "$EXTERNAL_DIR/makoureactor"
clone_or_update "https://github.com/sithlord48/ff7tk.git" "$EXTERNAL_DIR/ff7tk"
clone_or_update "https://github.com/individualcontributordev/Final-Fantasy-7-CSR.git" "$EXTERNAL_DIR/Final-Fantasy-7-CSR"
clone_or_update "https://github.com/individualcontributordev/individualcontributordev.github.io.git" "$EXTERNAL_DIR/individualcontributordev.github.io"
clone_or_update "https://github.com/Xeeynamo/ff7-decomp.git" "$EXTERNAL_DIR/ff7-decomp"
clone_or_update "https://github.com/AceZephyr/big-shoes.git" "$EXTERNAL_DIR/big-shoes"
clone_or_update "https://github.com/AceZephyr/FF7WorldMap.git" "$EXTERNAL_DIR/FF7WorldMap"

echo "==> Done. Reference repos are in $EXTERNAL_DIR (gitignored)."
