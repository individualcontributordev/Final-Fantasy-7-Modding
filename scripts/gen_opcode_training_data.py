#!/usr/bin/env python3
"""Generates explicit opcode fact Q&A training rows from ff7_opcodes.py's
OPCODE_NAMES/OPCODE_LENGTH arrays and appends them to
data/ff7_re_dataset.jsonl in the existing {instruction,input,output} schema.

Rationale: the model can retrieve OPCODE_NAMES/OPCODE_LENGTH source text via
RAG, but computing "name at index 0xF8" + "length at index 0xF8" requires
array-index arithmetic over a chunked/truncated source file, which the model
does unreliably (observed rambling/hallucination in eval_greedy_test.py).
Pre-computing every (hex, name, length) fact as a direct training example
turns this into memorized lookup instead of on-the-fly computation.

Ground truth: scripts/ff7_opcodes.py (from Makou Reactor's Opcode.cpp).
Idempotent: skips generation if these facts were already appended (checks
for a marker instruction already present in the dataset).
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
from ff7_opcodes import OPCODE_NAMES, OPCODE_LENGTH  # noqa: E402

DATASET_PATH = os.path.join(REPO_ROOT, "data", "ff7_re_dataset.jsonl")
FACTS_CORPUS_PATH = os.path.join(REPO_ROOT, "data", "ff7_opcode_facts.txt")
SOURCE_CITE = "scripts/ff7_opcodes.py (Makou Reactor Opcode.cpp ground truth)"
MARKER = "OPCODE_FACT_TABLE_V1"


def write_facts_corpus():
    """Writes a flat, RAG-chunkable text corpus (one line per opcode) so
    retrieval can surface direct (hex, name, length) facts instead of only
    the raw OPCODE_NAMES/OPCODE_LENGTH source arrays. Always overwritten
    (idempotent, deterministic from ff7_opcodes.py)."""
    lines = [
        "FF7 field script opcode facts (source: scripts/ff7_opcodes.py, "
        "Makou Reactor Opcode.cpp ground truth).",
        "Format: 0xHH = NAME, instruction length N byte(s) (1 opcode byte + M operand byte(s)).",
        "",
    ]
    for i, name in enumerate(OPCODE_NAMES):
        length = OPCODE_LENGTH[i]
        lines.append(
            f"0x{i:02X} = {name}, instruction length {length} byte(s) "
            f"(1 opcode byte + {length - 1} operand byte(s))."
        )
    os.makedirs(os.path.dirname(FACTS_CORPUS_PATH), exist_ok=True)
    with open(FACTS_CORPUS_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"✅ Wrote {len(OPCODE_NAMES)}-line opcode fact corpus to {FACTS_CORPUS_PATH}")


def make_single_opcode_row(idx: int) -> dict:
    name = OPCODE_NAMES[idx]
    length = OPCODE_LENGTH[idx]
    hexcode = f"0x{idx:02X}"
    operand_bytes = length - 1
    instruction = (
        f"In an FF7 field script, what opcode has the byte value {hexcode}, "
        f"and how many bytes does the full instruction (opcode + operands) occupy?"
    )
    thinking = (
        f"OPCODE_NAMES[{idx}] is '{name}' and OPCODE_LENGTH[{idx}] is {length}, "
        f"per {SOURCE_CITE}. Length {length} includes the 1-byte opcode itself, "
        f"so the operand payload is {operand_bytes} byte(s)."
    )
    output = (
        f"<thinking>\n{MARKER}: {thinking}\n</thinking>\n"
        f"Opcode {hexcode} is `{name}`. The full instruction is {length} byte(s) long "
        f"(1 opcode byte + {operand_bytes} operand byte(s))."
    )
    return {"instruction": instruction, "input": SOURCE_CITE, "output": output}


def make_walk_row(start_idx: int, indices: list) -> dict:
    """Generates a multi-opcode 'walk this byte sequence' example that chains
    consecutive opcodes at the given indices, matching eval_greedy_test.py's
    out-of-distribution byte-walk prompt style."""
    seq_bytes = []
    steps = []
    offset = 0
    for i in indices:
        name = OPCODE_NAMES[i]
        length = OPCODE_LENGTH[i]
        seq_bytes.append(f"{i:02X}")
        # Pad remaining operand bytes with 00 so the sequence is well-formed.
        seq_bytes.extend(["00"] * (length - 1))
        steps.append(f"offset {offset}: opcode {i:02X} = `{name}`, length {length}")
        offset += length
    byte_str = " ".join(seq_bytes)
    instruction = (
        f"Walk this raw byte sequence from a field script block: {byte_str}. "
        f"Identify each opcode by its leading byte, and state its offset, name, "
        f"and length in sequence."
    )
    thinking = (
        f"{MARKER}: Each step's opcode byte indexes into OPCODE_NAMES/OPCODE_LENGTH "
        f"from {SOURCE_CITE}; the next opcode starts at offset += length(current).\n"
        + "\n".join(steps)
    )
    output = (
        f"<thinking>\n{thinking}\n</thinking>\n"
        + "\n".join(steps)
        + f"\nTotal sequence length: {offset} bytes."
    )
    return {"instruction": instruction, "input": SOURCE_CITE, "output": output}


def main():
    write_facts_corpus()

    if os.path.exists(DATASET_PATH):
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            if MARKER in f.read():
                print(f"⚠️  {MARKER} rows already present in {DATASET_PATH}; skipping to avoid duplicates.")
                return

    rows = [make_single_opcode_row(i) for i in range(len(OPCODE_NAMES))]

    # A handful of multi-opcode byte-walk examples covering common field-script
    # patterns (movie/message/control-flow/math), including the exact opcodes
    # (0x60 MAPJUMP, 0x01 REQ) the eval script's byte-walk prompt used.
    walk_index_sets = [
        [0x60, 0x01, 0x08],           # MAPJUMP, REQ, JOIN
        [0xF8, 0xF9],                 # PMVIE, MOVIE
        [0x40, 0x48, 0x49],           # MESSAGE, ASK, MENU
        [0x85, 0x89, 0x8B],           # PLUS, MUL, DIV
        [0x10, 0x14, 0x00],           # JMPF, IFUB, RET
    ]
    rows.extend(make_walk_row(0, idxs) for idxs in walk_index_sets)

    os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)
    with open(DATASET_PATH, "a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"✅ Appended {len(rows)} opcode-fact training rows to {DATASET_PATH}")
    print(f"   ({len(OPCODE_NAMES)} single-opcode facts + {len(walk_index_sets)} byte-walk examples)")


if __name__ == "__main__":
    main()
