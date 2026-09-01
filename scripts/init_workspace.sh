#!/usr/bin/env bash
# Clone sibling repos next to this checkout, then remind where pristine discs go.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PARENT="$(cd "$HERE/.." && pwd)"
HOST="${FF7_GIT_HOST:-github.com-individualcontributordev}"

clone_sibling() {
    local name="$1"
    local dest="$PARENT/$name"
    if [ -d "$dest/.git" ]; then
        echo "==> $name already present at $dest"
        return
    fi
    echo "==> Cloning $name into $dest"
    git clone "git@${HOST}:individualcontributordev/${name}.git" "$dest"
}

clone_sibling Final-Fantasy-7-CSR
clone_sibling individualcontributordev.github.io

mkdir -p "$HERE/workspace/pristine"
echo "==> Copy NTSC-U images to:"
echo "    $HERE/workspace/pristine/FINALFANTASY7_D1.bin"
echo "    $HERE/workspace/pristine/FINALFANTASY7_D2.bin"
echo "    $HERE/workspace/pristine/FINALFANTASY7_D3.bin"
echo "==> Workspace layout is README.md."
