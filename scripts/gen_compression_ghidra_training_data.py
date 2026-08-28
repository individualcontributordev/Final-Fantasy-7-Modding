#!/usr/bin/env python3
"""Generates training rows for two zero-coverage domains the user flagged as
high priority: texture/LZS/archive compression (burning bins, console
hardware testing) and Ghidra debugging workflows. Appends to
data/ff7_re_dataset.jsonl in the existing {instruction,input,output} schema.

Ground truth sources (per AGENTS.md rule 1 — no invented facts):
- scripts/lzs.py (Okumura/ff7tk LZS::compress/decompress port)
- scripts/compress_gzipps.py (GZIPPS overlay recompression)
- docs/05-ghidra-guide.md, docs/06-ghidra-automation.md (Ghidra FIELD.BIN workflow)
- docs/07-hardware-burn.md (verification ladder / ImgBurn / MechaPwn burn steps)

Idempotent: skips generation if the marker instruction is already present.
"""
import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(REPO_ROOT, "data", "ff7_re_dataset.jsonl")
MARKER = "COMPRESSION_GHIDRA_FACT_V1"

LZS_CITE = "scripts/lzs.py (Okumura/ff7tk LZS::compress/decompress port)"
GZIPPS_CITE = "scripts/compress_gzipps.py"
GHIDRA_GUIDE_CITE = "docs/05-ghidra-guide.md"
GHIDRA_AUTO_CITE = "docs/06-ghidra-automation.md"
BURN_CITE = "docs/07-hardware-burn.md"


def row(instruction, input_cite, thinking, answer):
    output = f"<thinking>\n{MARKER}: {thinking}\n</thinking>\n{answer}"
    return {"instruction": instruction, "input": input_cite, "output": output}


def build_rows():
    rows = []

    # --- LZS decompression format ---
    rows.append(row(
        "How does FF7's LZS decompression algorithm decide whether the next "
        "output byte is a literal or a back-reference copy?",
        LZS_CITE,
        "decompress_all() maintains a control-bit accumulator 'first_byte'. "
        "It right-shifts first_byte each iteration; when bit 8 (0x100) becomes "
        "0, it refills first_byte from the next input byte OR'd with 0xFF00 "
        "(so the top byte tracks 8 remaining control bits). Bit 0 of the "
        "current first_byte, after shifting, decides literal (bit set) vs "
        "match (bit clear) for that slot.",
        "A control-bit stream drives it: 8 control bits are packed per marker "
        "byte (loaded as `data[i] | 0xFF00`, then right-shifted once per "
        "decision). If the low bit is 1, the next byte is a literal copied "
        "straight to output. If it's 0, the next 2 bytes encode a "
        "back-reference into a 4096-byte ring buffer instead."
    ))
    rows.append(row(
        "In FF7's LZS format, how is a back-reference match encoded in the "
        "2-byte (non-literal) case, and what is the ring buffer size?",
        LZS_CITE,
        "From decompress_all(): b1, b2 = data[i], data[i+1]; "
        "offset = b1 | ((b2 & 0xF0) << 4); end = (b2 & 0x0F) + 2 + offset. "
        "text_buf is a 4096-byte ring buffer (`cur` and `pos` are masked with "
        "& 4095). So offset is a 12-bit ring-buffer position (low 8 bits from "
        "b1, high 4 bits from the top nibble of b2), and match length is "
        "(b2 & 0x0F) + 2 (minimum match length 2, since 0x0 encodes length 2).",
        "Ring buffer size is 4096 bytes (positions wrap with `& 4095`). Given "
        "bytes b1, b2: `offset = b1 | ((b2 & 0xF0) << 4)` is the 12-bit ring "
        "buffer read position, and match length is `(b2 & 0x0F) + 2` (so the "
        "low nibble of b2 encodes length-minus-2, giving a minimum match "
        "length of 2 and max of 17)."
    ))
    rows.append(row(
        "What is the initial cursor position ('cur'/'r') in FF7's LZS ring "
        "buffer before any data is written, and why isn't it 0?",
        LZS_CITE,
        "decompress_all() initializes `cur = 4078`, and compress_all() "
        "initializes `r = 4078` matching it. This isn't arbitrary: the "
        "original Okumura LZSS reference implementation reserves the last "
        "N - F - 1 = 4096 - 18 - 1 = 4077 bytes of the ring buffer as a "
        "pre-zeroed lookback region, and starts writing at position 4078 "
        "(one past that region) so early back-references have deterministic "
        "zero bytes to reference before real data exists.",
        "It starts at position **4078**, matching Okumura's reference LZSS "
        "layout: N=4096 (ring buffer size), F=18 (max match length), so "
        "N - F - 1 = 4077 bytes are pre-zeroed lookback space, and the write "
        "cursor begins right after that at offset 4078."
    ))
    rows.append(row(
        "What are the LZS compressor's tuning constants N, F, and THRESHOLD "
        "in scripts/lzs.py's compress_all(), and what does each control?",
        LZS_CITE,
        "From compress_all(): N = 4096 (ring buffer / dictionary size), "
        "F = 18 (max match length the binary tree search will return), "
        "THRESHOLD = 2 (matches of length <= THRESHOLD are emitted as a "
        "literal instead of a back-reference, since a 2-byte match reference "
        "costs the same or more than 1-2 literal bytes).",
        "N = 4096 is the ring buffer/dictionary size, F = 18 is the maximum "
        "match length the binary-tree matcher will find, and THRESHOLD = 2 "
        "means any match of length 2 or less is emitted as a literal instead "
        "of a 2-byte back-reference (not worth the encoding overhead)."
    ))
    rows.append(row(
        "Why does scripts/lzs.py warn against using a from-scratch hash-chain "
        "LZS encoder instead of the bit-exact Okumura binary-tree port, even "
        "though both round-trip correctly through the repo's own decompressor?",
        LZS_CITE,
        "The compress_all() docstring explains: a hash-chain encoder can pick "
        "different match/literal splits than the original PS1 encoder for the "
        "same input, and while that still decompresses correctly through this "
        "repo's own LZS decoder, it produced on-console corruption in practice "
        "(referenced: docs/findings/2026-07-25-force-stub-compressed.md and "
        "the LOST2 background-corruption regression). The exact bit-for-bit "
        "encoder behavior matters for compatibility with what the original "
        "game/tooling expects, not just round-trip correctness in isolation.",
        "Because round-trip correctness (compress→decompress gives back the "
        "original bytes) isn't sufficient — a hash-chain encoder can choose "
        "different literal/match splits than the real PS1 encoder, and that "
        "divergence caused actual on-console corruption previously (see the "
        "LOST2 background-corruption regression and "
        "docs/findings/2026-07-25-force-stub-compressed.md). The bit-exact "
        "Okumura binary-tree port avoids that risk entirely."
    ))
    rows.append(row(
        "If I need to patch a single byte inside a field script that's stored "
        "LZS-compressed, when can I NOT just patch the compressed bytes in "
        "place, per scripts/lzs.py's find_literal_body_offset()?",
        LZS_CITE,
        "find_literal_body_offset() walks the LZS stream and raises ValueError "
        "if the target decompressed byte offset falls inside a back-reference "
        "match run rather than being an independent literal. In that case, "
        "the byte doesn't have a corresponding single compressed byte of its "
        "own — it was reconstructed from an earlier run of bytes via the ring "
        "buffer copy, so changing it requires re-encoding the whole match "
        "(potentially resizing the compressed stream), not an in-place edit.",
        "You can't patch in place if the target decompressed-output offset "
        "was produced by a back-reference match rather than a literal byte — "
        "find_literal_body_offset() explicitly raises ValueError for this "
        "case ('cannot patch in place'), because that output byte is copied "
        "from an earlier position via the ring buffer, not stored as its own "
        "compressed byte. You'd need to recompress the whole payload instead."
    ))

    # --- GZIPPS overlay format ---
    rows.append(row(
        "What is the on-disk layout of a GZIPPS-compressed overlay like "
        "FIELD.BIN or WORLD.BIN, per scripts/compress_gzipps.py?",
        GZIPPS_CITE,
        "compress_gzipps() reads: dec_size = struct.unpack('<I', original[0:4]) "
        "(4-byte little-endian uncompressed size), gzip_subheader = "
        "original[4:8] (4 more header bytes preserved verbatim), then "
        "original_payload = original[8:] is the actual gzip-compressed member. "
        "GZIPPS_HEADER_SIZE = 8 confirms the split point.",
        "8-byte header + gzip payload: bytes 0-3 are a little-endian u32 "
        "holding the uncompressed size, bytes 4-7 are an opaque subheader "
        "preserved as-is when repacking, and everything from byte 8 onward is "
        "a standard gzip member (magic `1F 8B`, DEFLATE stream, CRC32 + size "
        "trailer)."
    ))
    rows.append(row(
        "When recompressing a patched GZIPPS overlay, why does "
        "scripts/compress_gzipps.py try many different zlib strategies and "
        "compression levels instead of just using the default?",
        GZIPPS_CITE,
        "_deflate_candidates() loops over compression levels 0-9 crossed with "
        "5 zlib strategies (default, filtered, huffman-only, RLE, fixed) plus "
        "stdlib gzip.compress at each level, and optionally zopfli if "
        "installed. _best_gzip_payload() then picks whichever candidate "
        "produces valid output (round-trip verified via gzip.decompress) that "
        "best fits under prefer_payload_max (the original payload's size), "
        "falling back to the smallest overall if none fit. This matters "
        "because GZIPPS overlays are typically embedded at a fixed offset in "
        "a larger container (e.g. an ISO), so the recompressed patch must not "
        "grow past the original slot's size, or the tool has to relocate/grow "
        "the overlay instead of doing an in-place write.",
        "Because a patched overlay must not exceed the *original* compressed "
        "size (it usually occupies a fixed-size slot in a larger container), "
        "so the script brute-forces every zlib level (0-9) × strategy "
        "(default/filtered/huffman/RLE/fixed) plus stdlib gzip and optional "
        "zopfli, verifies each candidate round-trips to the exact patched "
        "bytes, and picks the smallest one that still fits within the "
        "original payload size — falling back to the smallest available if "
        "none fit, with a warning to install zopfli (which often shaves a few "
        "more bytes) if it's still too big."
    ))
    rows.append(row(
        "What happens in scripts/compress_gzipps.py if the best recompressed "
        "GZIPPS payload is still larger than the original slot?",
        GZIPPS_CITE,
        "In compress_gzipps(), size_delta = len(out) - len(original); if "
        "size_delta > 0, it prints a warning to stderr naming the chosen "
        "method and byte overage, suggests installing zopfli and re-running, "
        "and explicitly warns 'do NOT accept CDmage truncate' — listing "
        "options: (1) zopfli retry, (2) use a tool that can relocate/grow the "
        "overlay instead of in-place truncating, or (3) flag it for another "
        "approach. It still writes the oversized output but does not silently "
        "truncate it.",
        "It does NOT silently truncate the data. It writes the oversized "
        "output but prints an explicit warning naming the size overage and "
        "the method tried, and tells you not to accept a tool's offer to "
        "truncate (e.g. CDmage's 'truncate' prompt) — instead: try `pip "
        "install zopfli` and re-run (often saves a few bytes), or use a tool "
        "that can relocate/grow the overlay's container slot rather than "
        "truncating it in place."
    ))

    # --- Hardware burn / verification ladder ---
    rows.append(row(
        "What is the recommended verification ladder before calling an FF7 "
        "patch 'hardware-ready', per docs/07-hardware-burn.md?",
        BURN_CITE,
        "The doc lists 3 steps in order of increasing confidence and cost: "
        "(1) DuckStation Safe Mode — fast iteration, RAM watches, but weak for "
        "CD/timing/EDC issues; (2) MiSTer PSX FPGA core — near-real PS1 timing "
        "for Ghidra/Makou game-logic changes, but still weak for burned "
        "CD-R/MechaPwn/optical EDC issues; (3) burn + PS2 Slim 77003 "
        "(MechaPwn) — the only step that proves the actual disc image + burn "
        "+ real console, but slowest, so used last.",
        "A 3-step ladder, cheapest/fastest first: (1) **DuckStation Safe "
        "Mode** for fast iteration and RAM watches — but it can hide CD "
        "timing/EDC issues; (2) **MiSTer PSX FPGA core** for near-real PS1 "
        "timing on Ghidra/Makou logic changes — but it's weak for burned "
        "CD-R/MechaPwn/optical-EDC issues since it loads .bin/.cue from "
        "storage, not an optical drive; (3) **burn + PS2 Slim 77003 "
        "(MechaPwn)** — the only step that proves the real disc image, burn "
        "quality, and console together, used last since it's the slowest."
    ))
    rows.append(row(
        "Why can't MiSTer's PSX core replace burning a real CD-R for final "
        "verification, according to docs/07-hardware-burn.md?",
        BURN_CITE,
        "The doc states MiSTer loads .bin/.cue directly from storage, not "
        "through an optical drive, so it cannot catch ImgBurn burn-verify "
        "failures, MechaPwn boot quirks, media/laser compatibility issues, or "
        "optical EDC/ECC problems that only manifest with an actual burned "
        "disc in a real drive. It's described as 'strong evidence the mod "
        "logic will work on real PS1 hardware' but explicitly 'does not "
        "replace a burned CD-R on the PS2 for ImgBurn/EDC/media/laser issues'.",
        "Because MiSTer loads the `.bin`/`.cue` directly from storage rather "
        "than through an optical drive, so it can't catch burn-verify "
        "failures, laser/media compatibility, or optical EDC/ECC problems "
        "that only show up on a real burned disc. It's strong evidence the "
        "*game logic* (Ghidra/Makou patches) works on real PS1 hardware, but "
        "the PS2 Slim 77003 (MechaPwn) burn test is still required as the "
        "final gate for the physical disc itself."
    ))
    rows.append(row(
        "What ImgBurn settings does docs/07-hardware-burn.md specify for "
        "burning an FF7 disc image, and what mistake should be avoided?",
        BURN_CITE,
        "The doc's ImgBurn steps: use 'Write image file to disc', source must "
        "be the .cue file (not the .bin alone), write mode DAO "
        "(Disc-at-Once), speed 4x (try 8x only if 4x burns clean and you need "
        "it faster), and explicitly says do NOT 'ISO9660 data disc' the .bin "
        "as a plain file — FF7 is a raw MODE2/2352 PS1 CD image, and treating "
        "it as a generic data file would corrupt the sector format. Always "
        "run ImgBurn's verify pass before ejecting.",
        "Source the burn from the **`.cue`** file (never the `.bin` alone), "
        "use **Write image file to disc**, write mode **DAO (Disc-at-Once)**, "
        "and burn speed **4x** (only try 8x if 4x is clean and you need it "
        "faster). The critical mistake to avoid: do NOT treat the `.bin` as "
        "an 'ISO9660 data disc' file — FF7 is a raw `MODE2/2352` PS1 CD "
        "image, not a generic ISO9660 data file, and that path would corrupt "
        "the sector layout. Always run ImgBurn's verify pass before "
        "ejecting."
    ))
    rows.append(row(
        "After the disc builder applies patch layers, what regenerates the "
        "sector EDC/ECC, and what's the pass criterion before shipping a "
        "hardware burn?",
        BURN_CITE,
        "docs/07-hardware-burn.md states the disc builder (the website, not "
        "this repo) regenerates Mode2 Form1 EDC/ECC for every sector changed "
        "by applied layers. The pass criterion: new zips should ImgBurn-verify "
        "cleanly, and the doc notes this has been 'Confirmed on PS2 Slim "
        "77003 (MechaPwn): post-repair CSR+ Disc 1 burn loads and fields "
        "load.'",
        "The **disc builder website** (not a script in this repo) "
        "regenerates Mode2 Form1 EDC/ECC for every sector touched by applied "
        "patch layers. Pass criterion before shipping: the resulting zip's "
        "burn should **ImgBurn-verify cleanly**, and per the doc this exact "
        "post-repair flow was confirmed working on a PS2 Slim 77003 "
        "(MechaPwn) — CSR+ Disc 1 burn loads and fields load correctly."
    ))

    # --- Ghidra FIELD.BIN workflow ---
    rows.append(row(
        "What is the correct Ghidra import base address for FIELD.BIN.dec on "
        "US FF7, and what mistake was previously documented for this value?",
        GHIDRA_GUIDE_CITE,
        "docs/05-ghidra-guide.md's import settings table specifies base "
        "address 0x800A0000 for the US FIELD.BIN module, explicitly flagging "
        "that it 'was wrongly documented as 0x80000000' previously. It also "
        "gives a conversion for any existing project that used the wrong "
        "base: real VA = Ghidra_VA + 0xA0000 (e.g. table file offset 0x40638 "
        "maps to real address 0x800E0638).",
        "**0x800A0000** — this is called out because it was previously "
        "(incorrectly) documented as `0x80000000`. If you have an existing "
        "Ghidra project imported at the wrong base, the conversion is: real "
        "VA = Ghidra_VA + 0xA0000 (e.g. a Ghidra address of `0x40638` under "
        "the old wrong base corresponds to the real address `0x800E0638`). "
        "Prefer a fresh import at the correct base before trying to match "
        "DuckStation program counters."
    ))
    rows.append(row(
        "How do I locate FF7 FIELD.BIN's RNG table in Ghidra, and why can't "
        "I just search for xrefs to it afterward?",
        GHIDRA_GUIDE_CITE,
        "docs/05-ghidra-guide.md step 'First win': Search → Memory, search "
        "all, for the hex string B1 CA EE 6C 5A 71 2E 55 — this should give "
        "exactly one hit, marking the start of a 256-byte table (label it "
        "g_field_rng_table). Step 'Second win' warns explicitly: 'Do not "
        "rely on xrefs to the table — often 0 after default analysis' because "
        "MIPS code typically loads the table address via a lui/addiu pair "
        "that Ghidra's default analysis doesn't always link as a data "
        "reference. The workaround given is Search → For Scalars for known "
        "values (StepID / Offset / Danger) instead, then reading those "
        "functions for table loads.",
        "Search → Memory (search all) for the hex byte string "
        "`B1 CA EE 6C 5A 71 2E 55` — it should produce exactly one hit "
        "starting a 256-byte table; label it `g_field_rng_table`. You can't "
        "rely on xrefs to find code that uses it afterward because MIPS code "
        "typically loads the table's address via a `lui`/`addiu` pair that "
        "Ghidra's default analysis often fails to link as a data reference "
        "(xref count frequently shows 0 even though the table is used). "
        "Instead, use Search → For Scalars for known related values (StepID, "
        "Offset, Danger) and read those functions for table loads directly."
    ))
    rows.append(row(
        "What MIPS `lui` immediate and offset should I search for to find "
        "StepID references in US FIELD.BIN, and what's the resulting RAM "
        "address?",
        GHIDRA_GUIDE_CITE,
        "docs/05-ghidra-guide.md's 'Third win' section explicitly warns "
        "StepID is NOT encoded as lui 0x8009 + 0xc540 on the US build. "
        "Instead: search for lui …, 0x800a then an offset of -0x3ac0, which "
        "computes to 0x8009C540. The confirmed code site for this is around "
        "0x8000B9C8 (labeled increment_step_id), cross-referenced with "
        "01-encounter-system.md.",
        "Search for `lui …, 0x800a` paired with offset **-0x3ac0** — this "
        "computes to RAM address **0x8009C540** (StepID). Note the doc "
        "explicitly warns this is NOT `lui 0x8009` + `0xc540` on the US "
        "build, which is the naive-looking but wrong encoding. The confirmed "
        "code site using this is `increment_step_id` around `0x8000B9C8` "
        "(also documented in `docs/01-encounter-system.md`)."
    ))
    rows.append(row(
        "How do I confirm a Ghidra-identified function actually corresponds "
        "to the running game's encounter logic, using DuckStation, per "
        "docs/05-ghidra-guide.md's 'Fourth win'?",
        GHIDRA_GUIDE_CITE,
        "The doc's emulator correlation steps: load the test ISO in "
        "DuckStation, set a Debug break or memory watch at 0x8009C540 (the "
        "StepID RAM address found earlier), walk on a grass field in-game "
        "until StepID changes, note the program counter (PC) at that moment, "
        "then in Ghidra use Navigation → Go To that PC address — it should "
        "land inside or near the encounter check code. If the PC doesn't "
        "match any sensible Ghidra address, the import base address is "
        "likely wrong and needs adjusting before re-analyzing.",
        "1) In DuckStation, load the test ISO and set a Debug memory watch/"
        "breakpoint at `0x8009C540` (StepID). 2) Walk on a hostile/grass "
        "field in-game until StepID changes and note the PC (program "
        "counter) at that exact moment. 3) In Ghidra, Navigation → Go To "
        "that PC address — it should land inside or near the encounter check "
        "function. If the PC doesn't correspond to sensible code in Ghidra, "
        "your import base address is wrong; adjust it and re-run analysis "
        "before continuing."
    ))
    rows.append(row(
        "What Ghidra import settings should I use for a field script .DAT "
        "file like LOST2.DAT (not FIELD.BIN itself), and why differ from the "
        "FIELD.BIN MIPS import?",
        GHIDRA_GUIDE_CITE,
        "docs/05-ghidra-guide.md's 'Exporting Field Script Data' section: "
        "extract the decompressed field script with "
        "scripts/extract_field_dat.py, then import into Ghidra as Format "
        "'Raw Binary', Language 'Data:LE:8:default' (explicitly NOT MIPS — "
        "field scripts are bytecode, not MIPS machine code), base address "
        "0x00000000 relative to the file start. This differs from the "
        "FIELD.BIN import (MIPS R3000, base 0x800A0000) because FIELD.BIN "
        "contains actual executable MIPS code plus data, while a field "
        "script .DAT is a separate bytecode format interpreted by the "
        "engine, not directly-executed machine instructions.",
        "Format: **Raw Binary**, Language: **Data:LE:8:default** (explicitly "
        "*not* MIPS — field scripts are interpreted bytecode, not executable "
        "MIPS machine code), base address `0x00000000` relative to the file "
        "start. This differs from the FIELD.BIN import (MIPS R3000 32-bit LE, "
        "base `0x800A0000`) because FIELD.BIN itself is real executable code "
        "the PS1 CPU runs, while a field script .DAT is a bytecode stream the "
        "engine's script interpreter reads — Ghidra should treat it as plain "
        "data, not disassemble it as MIPS."
    ))
    rows.append(row(
        "What is the generic Ghidra recipe for checking whether a literal "
        "value (a filename, ID, or LBA) is hardcoded somewhere in an imported "
        "binary, and what does a zero-hit result actually mean?",
        GHIDRA_GUIDE_CITE,
        "docs/05-ghidra-guide.md's 'Reusable technique' section: use Search → "
        "For Strings (check 'Search all'/'Search all blocks' if offered, "
        "don't limit to already-defined strings) for text literals, or "
        "Search → For Scalars for numeric literals. If found, right-click the "
        "hit → References → Show References to Address (or Ctrl+Shift+F) to "
        "see every xref/caller, then decompile the containing function "
        "(Ctrl+E or right-click → Decompile). To scope a scalar search to one "
        "function, right-click it in Listing → Select Function, then run the "
        "scalar search restricted to that selection. Critically: the doc "
        "warns zero hits does NOT mean 'not hardcoded' — it can mean the "
        "value is computed at runtime rather than stored as a literal, and "
        "that distinction should be reported plainly rather than treated as "
        "a negative result.",
        "Search → For Strings (enable 'Search all'/'Search all blocks' if "
        "available — don't limit to already-defined strings) for text, or "
        "Search → For Scalars for numbers. On a hit, right-click → "
        "References → Show References to Address (`Ctrl+Shift+F`) to list "
        "every caller, then decompile each (`Ctrl+E` or right-click → "
        "Decompile). To scope a scalar search to one function: right-click "
        "it in the Listing → Select Function, then re-run the scalar search "
        "restricted to that selection. Important: a **zero-hit result does "
        "not prove the value isn't hardcoded** — it can mean the value is "
        "computed at runtime instead of stored as a literal constant; report "
        "that distinction explicitly rather than treating an empty search as "
        "a definitive negative."
    ))
    rows.append(row(
        "What does the Ghidra automation pipeline in "
        "docs/06-ghidra-automation.md commit to the repo, and what does it "
        "deliberately exclude, and why?",
        GHIDRA_AUTO_CITE,
        "The doc's 'What Gets Committed' section: committed are structured "
        "metadata JSON files (function addresses/sizes, symbol names/"
        "locations, control flow info, call graphs, data structure layouts) "
        "under workspace/ghidra-analysis/. Explicitly NOT committed: "
        "decompiled source code, full disassembly listings, original game "
        "binaries, or Ghidra project files. The stated rationale is that "
        "committing raw decompiled game code isn't appropriate, while "
        "structured metadata lets the Agent query function addresses/xrefs "
        "in future sessions without needing local Ghidra access or shipping "
        "copyrighted game code.",
        "**Committed:** structured JSON metadata under "
        "`workspace/ghidra-analysis/` — function addresses/sizes, symbol "
        "names/locations, control-flow info, call graphs, and data structure "
        "layouts. **Not committed:** decompiled source code, full "
        "disassembly listings, original game binaries, or Ghidra project "
        "files. The reasoning: committing raw decompiled game code isn't "
        "appropriate (copyright/practicality), whereas structured metadata "
        "lets the agent look up addresses, symbols, and call relationships in "
        "later sessions without needing local Ghidra access or the game "
        "binary itself."
    ))
    rows.append(row(
        "What checklist of FIELD.BIN functions/symbols has already been "
        "identified and confirmed in docs/05-ghidra-guide.md, with their "
        "addresses?",
        GHIDRA_GUIDE_CITE,
        "The doc's 'Functions to identify (checklist)' section lists 8 "
        "confirmed items: g_field_rng_table (data, 256 bytes @ 0x800E0638), "
        "increment_step_id (returns table[stepid]-offset @ 0x800AB9C8), "
        "increment_formation (@ 0x800ABA34, uses DAT_80071c20 + "
        "g_field_rng_table), encounter_check (0x800ABA70, Danger +=, dual "
        "RNG, formation pick), g_danger (renamed via lhu @ 0x800ABC1C, RAM "
        "0x8007173C), g_step_fraction (renamed via lbu @ 0x800ABAB4, RAM "
        "0x8009C6D8), field_main_loop (FUN_800a16cc @ 0x800A16CC, post-battle "
        "Danger clear), field_map_init (@ 0x800BA534, setup block "
        "LAB_800a1dc8 / 0x800A1DC8).",
        "All 8 are marked confirmed (checked off) in the guide: "
        "`g_field_rng_table` (256-byte table @ `0x800E0638`), "
        "`increment_step_id` (@ `0x800AB9C8`), `increment_formation` "
        "(@ `0x800ABA34`), `encounter_check` (@ `0x800ABA70` — Danger "
        "accumulation, dual RNG rolls, formation selection), `g_danger` "
        "(RAM `0x8007173C`, renamed via an `lhu` at `0x800ABC1C`), "
        "`g_step_fraction` (RAM `0x8009C6D8`, renamed via an `lbu` at "
        "`0x800ABAB4`), `field_main_loop` (`0x800A16CC`, clears Danger "
        "post-battle), and `field_map_init` (@ `0x800BA534`, setup block at "
        "`LAB_800a1dc8` / `0x800A1DC8`)."
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

    print(f"✅ Appended {len(rows)} compression/Ghidra training rows to {DATASET_PATH}")


if __name__ == "__main__":
    main()
