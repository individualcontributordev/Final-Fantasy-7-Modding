#!/usr/bin/env python3
"""Builds the RAG index (chunks.jsonl + embeddings.npz) from vendored RE
reference repos under external/ (see scripts/init_external_repos.sh) plus
this repo's own scripts/.

Portable by design: every chunk's "source" path is stored RELATIVE to the
repo root (e.g. "external/makoureactor/src/field.cpp"), so the committed
index works identically regardless of which machine built it or where the
source repos are physically cloned.

Usage (from repo root):
    source .venv_rag/bin/activate   # or any venv with sentence-transformers
    python3 scripts/build_rag_index.py

Outputs:
    rag_index/chunks.jsonl     - one JSON object per chunk (text, source, lines)
    rag_index/embeddings.npz   - float32 array, shape (num_chunks, 384)
"""
import json
import os

import numpy as np
from sentence_transformers import SentenceTransformer

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO_ROOT, "rag_index")
MODEL_NAME = "all-MiniLM-L6-v2"

# Directories (relative to repo root) to index.
SOURCE_DIRS = [
    "external/makoureactor",
    "external/ff7tk",
    "external/Final-Fantasy-7-CSR",
    "external/individualcontributordev.github.io",
    "external/ff7-decomp",
    "external/big-shoes",
    "external/FF7WorldMap",
    "external/ffvii",
    "external/ff7-chocobo",
    "external/ff7-coaster",
    "external/ff7-landscaper/src",
    "external/ff7-landscaper/docs",
    "external/q-gears/SupportedGames/FinalFantasy7",
    "external/q-gears/utilities/ffvii_battle_model_exporter",
    "external/q-gears/utilities/ffvii_battle_scene_dumper",
    "external/q-gears/utilities/ffvii_field_dat_dumper",
    "external/q-gears/utilities/ffvii_field_model_exporter",
    "external/q-gears/utilities/ffvii_field_model_exporter_pc",
    "external/q-gears/utilities/ffvii_font_exporter",
    "external/q-gears/utilities/ffvii_sound_dumper",
    "external/q-gears/utilities/ffvii_sound_dumper_psf",
    "external/q-gears/utilities/flevel",
    "external/q-gears/utilities/lzs",
    "external/q-gears_reverse/ffvii",
    "scripts",
    "data",
]

# File extensions worth chunking (source/docs; skip binaries, images, build junk).
# NOTE: ".ts" is ambiguous across our sources -- Qt Linguist translation XML
# (French/Japanese/Chinese/etc. UI strings) in makoureactor vs. real
# TypeScript in ff7-landscaper. Both are included below since the Qt ".ts"
# files all live under "/translations/", which EXCLUDE_PATH_SUBSTRINGS
# filters out regardless of extension.
INCLUDE_EXT = {
    ".c", ".h", ".cpp", ".hpp", ".cc", ".cxx",
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".cs", ".html", ".md", ".txt",
}

# Path substrings that mean "skip this file even if extension matches" --
# Qt translation catalogs (UI string localization, no RE content), and
# ff7-landscaper's node_modules/lockfile noise.
EXCLUDE_PATH_SUBSTRINGS = ("/translations/", "/node_modules/")

SKIP_DIR_NAMES = {".git", "node_modules", "build", "dist", "__pycache__", ".venv_rag", "rag_index"}

# Source-tier weighting: code chunks are more likely to answer RE questions
# than raw chat-log/discussion dumps competing for the same top_k slots.
CODE_EXTS = {".c", ".h", ".cpp", ".hpp", ".cc", ".cxx", ".py", ".js", ".jsx", ".tsx", ".cs"}

CHUNK_LINES = 60
OVERLAP_LINES = 10


def iter_source_files():
    seen_stems = set()  # (dirname, basename-without-ext) already yielded, for .md/.txt dedupe
    all_files = []
    for rel_dir in SOURCE_DIRS:
        abs_dir = os.path.join(REPO_ROOT, rel_dir)
        if not os.path.isdir(abs_dir):
            print(f"⚠️  Skipping missing dir: {rel_dir}")
            continue
        for dirpath, dirnames, filenames in os.walk(abs_dir):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
            for fname in filenames:
                ext = os.path.splitext(fname)[1].lower()
                if ext not in INCLUDE_EXT:
                    continue
                abs_path = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(abs_path, REPO_ROOT)
                if any(sub in rel_path.replace(os.sep, "/") for sub in EXCLUDE_PATH_SUBSTRINGS):
                    continue
                all_files.append((rel_path, abs_path))

    # De-duplicate .md/.txt pairs that are the same content dumped twice
    # under two extensions (e.g. "chat-log.md" + "chat-log.txt"). Prefer .md.
    by_stem = {}
    for rel_path, abs_path in all_files:
        root, ext = os.path.splitext(rel_path)
        if ext.lower() in (".md", ".txt"):
            by_stem.setdefault(root, []).append((ext.lower(), rel_path, abs_path))
        else:
            yield rel_path, abs_path

    for root, variants in by_stem.items():
        exts = {v[0] for v in variants}
        if ".md" in exts and ".txt" in exts:
            chosen = next(v for v in variants if v[0] == ".md")
        else:
            chosen = variants[0]
        yield chosen[1], chosen[2]


def chunk_file(rel_path, abs_path):
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"⚠️  Could not read {rel_path}: {e}")
        return

    if not lines:
        return

    step = CHUNK_LINES - OVERLAP_LINES
    for start in range(0, len(lines), step):
        end = min(start + CHUNK_LINES, len(lines))
        text = "".join(lines[start:end]).strip()
        if len(text) < 20:
            continue
        ext = os.path.splitext(rel_path)[1].lower()
        yield {
            "text": text,
            "source": rel_path,
            "line_start": start + 1,
            "line_end": end,
            "tier": "code" if ext in CODE_EXTS else "discussion",
        }
        if end == len(lines):
            break


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    chunks = []
    for rel_path, abs_path in iter_source_files():
        chunks.extend(chunk_file(rel_path, abs_path))

    if not chunks:
        print("❌ No chunks produced — check SOURCE_DIRS / that external/ repos are cloned.")
        return

    print(f"📦 Chunked {len(chunks)} chunks from {len(SOURCE_DIRS)} source dirs.")

    print(f"🧠 Loading embedding model: {MODEL_NAME} (CPU)...")
    model = SentenceTransformer(MODEL_NAME, device="cpu")

    texts = [c["text"] for c in chunks]
    print("🔢 Embedding chunks (this may take a few minutes)...")
    embeddings = model.encode(
        texts, batch_size=64, show_progress_bar=True, convert_to_numpy=True
    ).astype(np.float32)

    chunks_path = os.path.join(OUT_DIR, "chunks.jsonl")
    with open(chunks_path, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    emb_path = os.path.join(OUT_DIR, "embeddings.npz")
    np.savez_compressed(emb_path, embeddings=embeddings, model=MODEL_NAME)

    print(f"✅ Wrote {chunks_path} ({len(chunks)} chunks)")
    print(f"✅ Wrote {emb_path} (shape={embeddings.shape})")


if __name__ == "__main__":
    main()
