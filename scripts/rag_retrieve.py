#!/usr/bin/env python3
"""Loads the committed RAG index (rag_index/chunks.jsonl + embeddings.npz)
and retrieves the top-k most relevant chunks for a query via cosine
similarity. Designed to be imported by run_ff7_agent.py.

Index must already exist (built via scripts/build_rag_index.py, committed
to the repo). This module is read-only at runtime — it never re-embeds the
corpus, only the incoming query.
"""
import json
import os

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_DIR = os.path.join(REPO_ROOT, "rag_index")
CHUNKS_PATH = os.path.join(INDEX_DIR, "chunks.jsonl")
EMB_PATH = os.path.join(INDEX_DIR, "embeddings.npz")

_model = None
_chunks = None
_embeddings = None


def _load_index():
    global _chunks, _embeddings
    if _chunks is not None and _embeddings is not None:
        return
    if not (os.path.exists(CHUNKS_PATH) and os.path.exists(EMB_PATH)):
        raise FileNotFoundError(
            f"RAG index not found at {INDEX_DIR}. "
            f"Run scripts/build_rag_index.py first (or pull the committed index)."
        )
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        _chunks = [json.loads(line) for line in f if line.strip()]
    data = np.load(EMB_PATH)
    _embeddings = data["embeddings"]
    if len(_chunks) != _embeddings.shape[0]:
        raise ValueError(
            f"chunks.jsonl ({len(_chunks)} rows) and embeddings.npz "
            f"({_embeddings.shape[0]} rows) are out of sync. Rebuild the index."
        )


def _get_model(model_name="all-MiniLM-L6-v2"):
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(model_name, device="cpu")
    return _model


def retrieve(query, top_k=4, min_score=0.25, code_boost=0.03):
    """Returns up to top_k chunks (dicts with text/source/line_start/line_end/score)
    for the given query, sorted by descending cosine similarity. Chunks below
    min_score are dropped (avoids injecting irrelevant context when nothing
    in the corpus is actually related).

    code_boost: small additive bump to cosine score for chunks tagged
    tier="code" (vs. "discussion", e.g. chat-log dumps). Code chunks are more
    likely to answer RE questions; without this, high-volume discussion
    chunks can crowd out code chunks of similar semantic relevance for the
    same top_k slots. Set to 0 to disable."""
    _load_index()
    model = _get_model()

    query_vec = model.encode([query], convert_to_numpy=True).astype(np.float32)[0]

    # Cosine similarity: normalize both sides.
    corpus_norms = np.linalg.norm(_embeddings, axis=1)
    query_norm = np.linalg.norm(query_vec)
    if query_norm == 0 or np.any(corpus_norms == 0):
        return []

    sims = (_embeddings @ query_vec) / (corpus_norms * query_norm)
    if code_boost:
        tier_bonus = np.array(
            [code_boost if c.get("tier") == "code" else 0.0 for c in _chunks],
            dtype=np.float32,
        )
        ranked = sims + tier_bonus
    else:
        ranked = sims
    top_idx = np.argsort(-ranked)[:top_k]

    results = []
    for i in top_idx:
        score = float(sims[i])
        if score < min_score:
            continue
        chunk = dict(_chunks[i])
        chunk["score"] = score
        results.append(chunk)
    return results


def format_context(results):
    """Formats retrieved chunks into a citeable context block for prompt injection."""
    if not results:
        return ""
    parts = []
    for r in results:
        cite = f"{r['source']}:{r['line_start']}-{r['line_end']}"
        parts.append(f"[SOURCE: {cite}]\n{r['text']}")
    return "\n\n".join(parts)


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "field script opcode jump"
    hits = retrieve(q)
    print(f"Query: {q}\n")
    for h in hits:
        print(f"[{h['score']:.3f}] {h['source']}:{h['line_start']}-{h['line_end']}")
        print(h["text"][:200].replace("\n", " ") + "...\n")
