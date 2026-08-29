#!/usr/bin/env python3
"""Generates RAG-SHAPED training rows to fix a train/inference distribution
mismatch diagnosed live: the LoRA was only ever trained on one-line source
citations (e.g. "scripts/lzs.py (Okumura port)") as "Input Context", but at
inference (run_ff7_agent.py) it's prompted with real multi-chunk RAG context
blocks formatted as "[SOURCE: file:start-end]\\n{raw text}". The model had
never learned to derive/constrain answers from a pasted raw-text block, so it
fell back on memorized-but-ungrounded arithmetic/filenames/mechanisms
(confabulation) even when the right base fact was present in context.

This generator re-implements build_rag_index.py's EXACT chunking algorithm
(CHUNK_LINES=60, OVERLAP_LINES=10) against the same three ground-truth files
already implicated in the live confabulation symptoms, so every "input"
context block here is byte-identical to what the real RAG index would
produce and cite -- not a hand-typed approximation. Rows are:

- Single-chunk grounded Q&A (most common real case).
- Multi-chunk rows with a DISTRACTOR chunk from an unrelated file appended,
  teaching the model to ignore irrelevant retrieved context instead of
  blending facts from it into the answer.
- "Not stated in source" rows, teaching abstention over confabulation when
  the provided chunk doesn't actually answer the question.

Idempotent: skips generation if the marker instruction is already present.
"""
import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(REPO_ROOT, "data", "ff7_re_dataset.jsonl")
MARKER = "RAG_SHAPED_FACT_V1"

CHUNK_LINES = 60
OVERLAP_LINES = 10

GHIDRA_GUIDE = "docs/05-ghidra-guide.md"
EDC_ECC = "scripts/edc_ecc.py"
LZS = "scripts/lzs.py"
GZIPPS = "scripts/compress_gzipps.py"  # used only as a distractor source


def chunk_file(rel_path):
    """Mirrors build_rag_index.py's chunk_file() exactly."""
    abs_path = os.path.join(REPO_ROOT, rel_path)
    with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    chunks = []
    step = CHUNK_LINES - OVERLAP_LINES
    for start in range(0, len(lines), step):
        end = min(start + CHUNK_LINES, len(lines))
        text = "".join(lines[start:end]).strip()
        if len(text) < 20:
            continue
        chunks.append({
            "source": rel_path,
            "line_start": start + 1,
            "line_end": end,
            "text": text,
        })
        if end == len(lines):
            break
    return chunks


def fmt_context(*chunks):
    """Mirrors rag_retrieve.format_context() exactly."""
    parts = []
    for c in chunks:
        cite = f"{c['source']}:{c['line_start']}-{c['line_end']}"
        parts.append(f"[SOURCE: {cite}]\n{c['text']}")
    return "\n\n".join(parts)


def row(instruction, context, thinking, answer):
    output = f"<thinking>\n{MARKER}: {thinking}\n</thinking>\n{answer}"
    return {"instruction": instruction, "input": context, "output": output}


def build_rows():
    g = chunk_file(GHIDRA_GUIDE)   # 5 chunks, [0]=1-60 [1]=51-110 [2]=101-160 [3]=151-210 [4]=201-238
    e = chunk_file(EDC_ECC)        # 3 chunks, [0]=1-60 [1]=51-110 [2]=101-152
    l = chunk_file(LZS)            # 6 chunks, [0]=1-60 [1]=51-110 [2]=101-160 [3]=151-210 [4]=201-260 [5]=251-293
    gz = chunk_file(GZIPPS)        # distractor only

    rows = []

    # --- Single-chunk grounded rows: exact prompt shape run_ff7_agent.py sends ---
    rows.append(row(
        "I imported FIELD.BIN into Ghidra at base address 0x80000000 and none "
        "of my known function addresses from prior notes line up. What's "
        "wrong, and what correction do I need to apply to every address I "
        "look up?",
        fmt_context(g[0]),
        "The [SOURCE: docs/05-ghidra-guide.md:1-60] chunk states the correct "
        "base is 0x800A0000, not 0x80000000, and gives the exact migration "
        "formula for an existing wrong-base project: real VA = Ghidra_VA + "
        "0xA0000 (worked example: file offset 0x40638 -> real 0x800E0638). "
        "Nothing else in this chunk is relevant to the question -- do not "
        "invent a different offset or arithmetic not stated here.",
        "You imported at the wrong base. Per `docs/05-ghidra-guide.md:1-60`, "
        "the correct base address for FIELD.BIN.dec (US) is **`0x800A0000`**, "
        "not `0x80000000`. Since you already imported at `0x80000000`, don't "
        "hand-adjust each address with new arithmetic -- either (a) re-import "
        "fresh at `0x800A0000` (recommended), or (b) apply the documented "
        "correction to every existing Ghidra address: **real VA = Ghidra_VA + "
        "0xA0000**. Worked example from the source: a Ghidra address of "
        "`0x40638` under the old wrong base becomes real address "
        "`0x800E0638`."
    ))
    rows.append(row(
        "According to the Ghidra guide, why can't I just search for xrefs to "
        "g_field_rng_table to find the code that uses it, and what should I "
        "search for instead?",
        fmt_context(g[0]),
        "This chunk explicitly states xrefs to the table are often 0 after "
        "default analysis because MIPS loads it via a lui/addiu pair Ghidra "
        "doesn't always link as a data reference, and directs using Search -> "
        "For Scalars for StepID/Offset/Danger instead.",
        "Because MIPS code typically loads the table's address via a "
        "`lui`/`addiu` pair, and per `docs/05-ghidra-guide.md:1-60` Ghidra's "
        "default analysis often fails to link that as a data reference -- "
        "xref count can show **0** even though the table is actually used. "
        "Instead, use **Search -> For Scalars** for known related values "
        "(StepID, Offset, Danger) and read those functions for the table "
        "load directly."
    ))
    rows.append(row(
        "What RAM address does StepID live at in US FIELD.BIN, and what "
        "Ghidra scalar search finds it, per the guide?",
        fmt_context(g[1]),
        "The [SOURCE: docs/05-ghidra-guide.md:51-110] chunk repeats the third "
        "win: search lui ..., 0x800a with offset -0x3ac0, giving 0x8009C540, "
        "confirmed site ~0x8000B9C8 (increment_step_id). The checklist below "
        "it lists related but distinct addresses (g_danger 0x8007173C, "
        "g_step_fraction 0x8009C6D8) -- must not conflate those with StepID.",
        "StepID lives at RAM address **`0x8009C540`**. Per "
        "`docs/05-ghidra-guide.md:51-110`, find it by searching for "
        "`lui ..., 0x800a` paired with offset **`-0x3ac0`**. The confirmed "
        "code site referencing it is `increment_step_id` around "
        "`~0x8000B9C8`. Don't confuse this with `g_danger` (`0x8007173C`) or "
        "`g_step_fraction` (`0x8009C6D8`), which are separate addresses "
        "listed nearby in the same checklist."
    ))
    rows.append(row(
        "What is the confirmed address of the encounter_check function in "
        "FIELD.BIN, and what does it do according to the checklist?",
        fmt_context(g[1]),
        "The checklist line in this chunk: encounter_check -- 0x800ABA70 "
        "(Danger +=, dual RNG, formation pick). No other function in this "
        "chunk shares that description.",
        "`encounter_check` is at **`0x800ABA70`** (per "
        "`docs/05-ghidra-guide.md:51-110`'s checklist), and it handles Danger "
        "accumulation (`Danger +=`), two RNG calls, and formation selection."
    ))

    # --- EDC/ECC chunks ---
    rows.append(row(
        "My ImgBurn verify pass fails after patching FIELD.BIN with a repair "
        "tool. What does EDC actually cover in a Mode 2 Form 1 sector, and "
        "where does repair_sector_edc_ecc() write the fixed value?",
        fmt_context(e[0], e[2]),
        "e[0] (1-60) is the module docstring/layout + compute_edc(); e[2] "
        "(101-152) has repair_sector_edc_ecc() which computes EDC over "
        "sector[16:2076] (header+subheader+data) and writes it little-endian "
        "into sector[2072:2076], then calls compute_ecc(). Nothing in either "
        "chunk mentions an 'on-the-fly ECC' hardware mechanism -- must not "
        "invent one.",
        "Per `scripts/edc_ecc.py:1-60` and `:101-152`: EDC is a CRC-32 "
        "(polynomial `0xD8018001`) computed over bytes 16-2075 of the "
        "2352-byte sector (the 4-byte header + 8-byte subheader + 2048 bytes "
        "of user data) via `compute_edc()`. `repair_sector_edc_ecc()` writes "
        "the recomputed value **little-endian into `sector[2072:2076]`**, "
        "then calls `compute_ecc()` to rebuild the following 276-byte ECC "
        "(P/Q parity) region. If ImgBurn's verify still fails after this "
        "repair runs, the mismatch is in what's feeding the repair (wrong "
        "sector boundaries, sectors not actually re-run through the repair "
        "step, or a build step overwriting sectors afterward) rather than in "
        "the EDC formula itself, which this source defines unambiguously."
    ))
    rows.append(row(
        "In compute_ecc(), how many P-parity and Q-parity vectors are there "
        "and how many bytes does each parity block occupy in the sector?",
        fmt_context(e[1]),
        "e[1] (51-110): P parity loop is range(86) each producing 2 bytes "
        "-> 172 bytes written to sector[2076:2248]. Q parity loop is "
        "range(52) each producing 2 bytes -> 104 bytes written to "
        "sector[2248:2352]. 172+104=276, matching the documented ECC size.",
        "**P parity**: 86 vectors, 2 bytes each = 172 bytes, written to "
        "`sector[2076:2248]`. **Q parity**: 52 vectors, 2 bytes each = "
        "104 bytes, written to `sector[2248:2352]`. Total 276 bytes, "
        "matching the ECC region size stated in `scripts/edc_ecc.py:51-110`."
    ))
    rows.append(row(
        "Does repair_sector_edc_ecc() do anything for Mode 2 Form 2 sectors "
        "(e.g. streaming audio/video sectors without EDC/ECC)?",
        fmt_context(e[2]),
        "e[2] (101-152): explicit early return 'if sector[16+2] & 0x20: "
        "return # Mode 2 Form 2, no EDC/ECC'. So it's a no-op for Form 2.",
        "No -- per `scripts/edc_ecc.py:101-152`, `repair_sector_edc_ecc()` "
        "checks subheader byte `sector[18]` (`16+2`): if bit `0x20` is set "
        "(Form 2), it returns immediately without touching the sector at "
        "all, since Form 2 sectors don't carry EDC/ECC in this layout."
    ))

    # --- LZS chunks ---
    rows.append(row(
        "In FF7's LZS decompressor, what ring buffer position does 'cur' "
        "start at, and does the compressor's starting position match it?",
        fmt_context(l[0]),
        "l[0] (1-60): decompress_all() sets cur = 4078 at the top. This "
        "chunk only covers the decompressor; the compressor's 'r' starting "
        "value isn't shown here, so I can only confirm the decompressor's "
        "value from this context, not assert the compressor matches without "
        "separate confirmation.",
        "In `decompress_all()` (`scripts/lzs.py:1-60`), the ring-buffer "
        "cursor `cur` starts at **4078**. This chunk doesn't include "
        "`compress_all()`'s starting `r` value, so I can't confirm from this "
        "excerpt alone whether the compressor matches -- that would need to "
        "be checked separately in the compressor's own source."
    ))
    rows.append(row(
        "Why does find_literal_body_offset() raise ValueError instead of "
        "returning an offset for some decompressed byte positions?",
        fmt_context(l[1], l[2]),
        "l[1] (51-110) has the start of find_literal_body_offset(); l[2] "
        "(101-160) has the raise ValueError(...) line for the "
        "back-reference-match case, with message 'cannot patch in place'.",
        "Per `scripts/lzs.py:51-110` and `:101-160`, `find_literal_body_offset()` "
        "raises `ValueError` when the requested decompressed-output offset "
        "falls **inside a back-reference match run** rather than landing on "
        "an independent literal byte. In that case there's no single "
        "compressed byte corresponding to that output position -- it was "
        "reconstructed from an earlier ring-buffer run -- so it explicitly "
        "cannot be patched in place ('cannot patch in place' is the literal "
        "message text)."
    ))
    rows.append(row(
        "What are N, F, and THRESHOLD set to in compress_all(), and what "
        "does the docstring say about why this is a bit-exact port rather "
        "than a from-scratch encoder?",
        fmt_context(l[2]),
        "l[2] (101-160) contains compress_all()'s docstring: bit-exact port "
        "of Okumura binary-tree LZSS used by ff7tk's LZS::compress(), "
        "because a prior from-scratch hash-chain encoder chose different "
        "match/literal splits that round-tripped through this repo's own "
        "decompressor but caused on-console corruption (cites "
        "docs/findings/2026-07-25-force-stub-compressed.md and the LOST2 "
        "regression). N/F/THRESHOLD values themselves are in the docstring "
        "text: N=4096, F=18, THRESHOLD=2.",
        "Per `scripts/lzs.py:101-160`: **N=4096** (ring buffer size), "
        "**F=18** (max match length), **THRESHOLD=2** (matches of length "
        "<=2 are emitted as literals). The docstring explains this is a "
        "*bit-exact* port of Okumura's binary-tree LZSS (matching ff7tk's "
        "`LZS::compress()`) specifically because a previous from-scratch "
        "hash-chain encoder could choose different match/literal splits for "
        "the same input -- which still round-trips correctly through this "
        "repo's own decompressor, but caused real **on-console corruption** "
        "(referenced: `docs/findings/2026-07-25-force-stub-compressed.md` "
        "and the LOST2 background-corruption regression). Round-trip "
        "correctness alone isn't sufficient; bit-exact encoder behavior is "
        "required for hardware compatibility."
    ))
    rows.append(row(
        "Walk through what insert_node() and delete_node() do in the LZS "
        "compressor's binary tree, per this source.",
        fmt_context(l[3]),
        "l[3] (151-210) contains the tail of insert_node() (tree rebalancing "
        "when replacing node p with r) and all of delete_node() (three "
        "cases: no right child, no left child, both children with "
        "predecessor-splice). This is dense pointer-manipulation code; I "
        "should describe structure, not invent semantics not shown.",
        "Per `scripts/lzs.py:151-210`: `insert_node()`'s tail handles "
        "replacing a node `p` in the binary tree with the new node `r` when "
        "`r` becomes the longest/best match found so far -- it re-parents "
        "`p`'s children (`lson[p]`, `rson[p]`) onto `r`, fixes up `r`'s "
        "parent link in whichever side of `dad[p]` originally pointed at "
        "`p`, then marks `p` removed (`dad[p] = NIL`). `delete_node()` "
        "removes a node from the tree with the standard 3-case BST deletion: "
        "if no right child, splice in the left child; if no left child, "
        "splice in the right child; otherwise find the in-order predecessor "
        "(rightmost node of the left subtree) and splice it into `p`'s "
        "position, relinking its own children first."
    ))

    # --- Distractor rows: irrelevant chunk from an unrelated file included ---
    rows.append(row(
        "What is the initial cursor position in FF7's LZS ring buffer "
        "before any data is written?",
        fmt_context(l[0], gz[0]),
        "The question is fully answered by l[0] (cur = 4078). gz[0] "
        "(scripts/compress_gzipps.py:1-60) is an unrelated GZIPPS "
        "recompression module included as a distractor -- it has nothing to "
        "do with LZS ring buffers and must be ignored, not blended in.",
        "**4078** -- per `scripts/lzs.py:1-60`, `decompress_all()` "
        "initializes `cur = 4078`. (The other retrieved chunk, "
        "`scripts/compress_gzipps.py:1-60`, covers GZIPPS overlay "
        "recompression and is unrelated to LZS or ring buffers; it doesn't "
        "apply to this question.)"
    ))
    rows.append(row(
        "What does compute_edc() in scripts/edc_ecc.py compute EDC over, "
        "argument-wise?",
        fmt_context(e[0], gz[1]),
        "e[0] shows compute_edc(data: bytes) computes CRC-32 over whatever "
        "'data' the caller passes (its own docstring says 'header + "
        "subheader + user data'). gz[1] (compress_gzipps.py:51-110) is an "
        "unrelated zlib-strategy-loop distractor chunk about GZIPPS "
        "recompression, not EDC -- ignore it.",
        "`compute_edc(data: bytes)` computes a CRC-32 (using the "
        "polynomial-0xD8018001 table) over whatever byte range the caller "
        "passes in as `data` -- per its docstring in "
        "`scripts/edc_ecc.py:1-60`, that's meant to be the sector's header + "
        "subheader + user data (bytes 16-2075, per how `repair_sector_edc_ecc()` "
        "calls it elsewhere in the file). The other retrieved chunk "
        "(`scripts/compress_gzipps.py:51-110`) covers zlib compression "
        "strategy selection for GZIPPS overlays and has no bearing on EDC "
        "computation; it's not relevant here."
    ))

    # --- "Not stated in source" rows: teach abstention over confabulation ---
    rows.append(row(
        "What does docs/05-ghidra-guide.md say the Ghidra decompiler's "
        "'Function Graph' view is used for during FIELD.BIN analysis?",
        fmt_context(g[3]),
        "g[3] (151-210) covers exporting field script data (hex dumps, byte "
        "strings, Intel Hex) -- it never mentions a 'Function Graph' view at "
        "all. The honest answer is that this isn't stated in the provided "
        "excerpt, not a guess at what such a view might plausibly do.",
        "The provided excerpt (`docs/05-ghidra-guide.md:151-210`) doesn't "
        "mention a 'Function Graph' view anywhere -- it covers exporting "
        "field script data (hex dumps, byte strings, Intel Hex exports) for "
        "patching purposes. I can't answer this from the given source; it "
        "isn't stated here."
    ))
    rows.append(row(
        "According to scripts/lzs.py, what is the maximum file size in "
        "bytes that FIELD/*.DAT field scripts are allowed to be?",
        fmt_context(l[4]),
        "l[4] (201-260) is the middle of compress_all()'s main matching "
        "loop (tree insert/delete bookkeeping) -- it defines no file-size "
        "limit for FIELD/*.DAT scripts anywhere. Must not invent a plausible "
        "number.",
        "Not stated in this excerpt (`scripts/lzs.py:201-260`) -- it's the "
        "middle of `compress_all()`'s match-search loop and doesn't define "
        "any maximum size for FIELD/*.DAT field script files. This source "
        "only covers the LZS compression algorithm's ring-buffer mechanics, "
        "not a file-size ceiling."
    ))
    rows.append(row(
        "Per scripts/edc_ecc.py, what happens if repair_image_edc_ecc() is "
        "called on an image whose length isn't a multiple of 2352 bytes?",
        fmt_context(e[2]),
        "e[2] shows repair_image_edc_ecc() computing total_sectors = "
        "len(img) // sector_size (integer division) and looping "
        "range(total_sectors) -- it silently truncates/ignores any trailing "
        "partial-sector bytes rather than raising an error. This chunk does "
        "not show any explicit warning or exception for this case, so I "
        "should describe the actual code behavior (silent truncation via "
        "integer division) without asserting a warning exists that isn't in "
        "the text.",
        "Per `scripts/edc_ecc.py:101-152`, `repair_image_edc_ecc()` computes "
        "`total_sectors = len(img) // sector_size` using integer division, "
        "then only loops over that many whole 2352-byte sectors. Any "
        "trailing bytes that don't form a complete sector are simply never "
        "touched -- the function doesn't raise an error or print a warning "
        "for a non-multiple-of-2352 length in this source; it silently "
        "leaves the leftover bytes unprocessed."
    ))

    return rows


def main():
    if os.path.exists(DATASET_PATH):
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            if MARKER in f.read():
                print(f"⚠️  {MARKER} rows already present in {DATASET_PATH}; skipping to avoid duplicates.")
                return

    rows = build_rows()
    with open(DATASET_PATH, "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"✅ Appended {len(rows)} RAG-shaped training rows to {DATASET_PATH}")


if __name__ == "__main__":
    main()
