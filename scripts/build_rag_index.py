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
    "scripts",
    "data",
]

# File extensions worth chunking (source/docs; skip binaries, images, build junk).
INCLUDE_EXT = {
    ".c", ".h", ".cpp", ".hpp", ".cc", ".cxx",
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".cs", ".html", ".md", ".txt",
}

SKIP_DIR_NAMES = {".git", "node_modules", "build", "dist", "__pycache__", ".venv_rag", "rag_index"}

CHUNK_LINES = 60
OVERLAP_LINES = 10


def iter_source_files():
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
                yield rel_path, abs_path


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
        yield {
            "text": text,
            "source": rel_path,
            "line_start": start + 1,
            "line_end": end,
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
