#!/usr/bin/env python3
"""Local test harness for the fine-tuned FF7 RE/modding model.

Prerequisite: run `python3 extract_game_assets.py` first to populate
`data/extracted_fields/` from the pristine disc images.

Honesty note: the byte offsets embedded below were found by scanning raw
byte VALUES (0x60 / 0x2B / 0x48) in the extracted .DAT files — they are
NOT proven to be decoded instruction boundaries from a real opcode-stream
walk starting at the script table. Treat "MAPJUMP-length instruction
starting near offset X" as a hypothesis the model should verify/derive,
not a pre-confirmed ground truth. Do not present harness output as more
certain than that.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from unsloth import FastLanguageModel
import torch
import sys

EXTRACTED_DIR = Path("data/extracted_fields")



# Cache the model instance globally so it only loads into VRAM once during the test sweep
_GLOBAL_MODEL = None
_GLOBAL_TOKENIZER = None

def call_local_model(prompt_string: str) -> str:
    """Dispatches the prompt to our fine-tuned RTX 3070 model layers and streams the text output."""
    global _GLOBAL_MODEL, _GLOBAL_TOKENIZER
    
    # 1. Lazy-load the model into memory on the first test call
    if _GLOBAL_MODEL is None:
        print("\n🧠 [TEST HARNESS]: Loading DeepSeek-R1-8B Base + Custom FF7 Adapters into VRAM...")
        max_seq_length = 4096
        
        # Load core 4-bit base model layers
        _GLOBAL_MODEL, _GLOBAL_TOKENIZER = FastLanguageModel.from_pretrained(
            model_name = "unsloth/DeepSeek-R1-Distill-Llama-8B",
            max_seq_length = max_seq_length,
            dtype = torch.float16,
            load_in_4bit = True,
        )
        
        # Dynamically lay your 1,348-row adapter layers straight over them
        _GLOBAL_MODEL.load_adapter("ff7_coder_lora_model")
        FastLanguageModel.for_inference(_GLOBAL_MODEL)
        print("✔ [TEST HARNESS]: Brain loaded successfully. Executing exercise matrix...")

    # 2. Structure the prompt to match our exact training system format
    full_prompt = f"### System:\nYou are an expert PlayStation 1 and Final Fantasy VII reverse engineering model.\n\n### Instruction:\n{prompt_string}\n\n### Response:\n"
    
    # 3. Tokenize and generate the text sequence on your RTX 3070
    inputs = _GLOBAL_TOKENIZER([full_prompt], return_tensors="pt").to("cuda")
    outputs = _GLOBAL_MODEL.generate(
        input_ids=inputs.input_ids,
        max_new_tokens=1024,
        use_cache=True
    )
   
    # FIX: Extract element [0] from the batch list BEFORE calling split()
    decoded_list = _GLOBAL_TOKENIZER.batch_decode(outputs)
    response_text = decoded_list[0].split("### Response:\n")[-1]
    
    return response_text.replace("</s>", "").strip()




def load_bytes(name: str) -> bytes:
    path = EXTRACTED_DIR / name
    if not path.is_file():
        raise SystemExit(
            f"missing {path} — run extract_game_assets.py first"
        )
    return path.read_bytes()


def build_exercises() -> list[dict]:
    fship = load_bytes("FSHIP_12.DAT")
    md8_5 = load_bytes("MD8_5.DAT")

    ex1_slice = fship[655:695].hex()
    ex3_ids = [67, 71, 731]

    return [
        {
            "name": "opcode_byte_parsing",
            "prompt": (
                "<thinking>\n"
                "Walk this raw hex slice pulled from FIELD/FSHIP_12.DAT "
                f"(byte offsets 655-695 of the extracted file): {ex1_slice}\n"
                "It contains bytes matching MAPJUMP (0x60, len 10), "
                "SLIP (0x2B, len 2), and ASK (0x48, len 7). Identify plausible "
                "instruction start offsets and lengths. Do not import any "
                "external opcode table — inline what you need.\n"
                "</thinking>\n"
            ),
        },
        {
            "name": "lba_correction_math",
            "prompt": (
                "<thinking>\n"
                "A mock .STR movie header stores a 32-bit little-endian byte "
                "offset at struct field `data_offset` = 0x0010A000. The movie "
                "is being swapped to start 16 sectors (2352 bytes/sector, "
                "RAW mode) later on disc. Compute the corrected LE32 value "
                "and emit the struct.pack call to write it, self-contained.\n"
                "</thinking>\n"
            ),
        },
        {
            "name": "maplist_graph_logic",
            "prompt": (
                "<thinking>\n"
                f"Runtime trace mentions field ids embedded messily: "
                f"'...jump seq id={ex3_ids[0]} then id={ex3_ids[1]} "
                f"finally id={ex3_ids[2]}...'. Resolve each to its map stem "
                "using an inlined MAPLIST_PARTIAL (no external import) and "
                "emit a JSON directed graph {nodes:[...], edges:[[from,to],...]} "
                "in id order given.\n"
                "</thinking>\n"
            ),
        },
    ]


def evaluate(name: str, response: str) -> dict:
    thinking_ok = bool(
        re.search(r"<thinking>.*?</thinking>", response, re.S)
    )
    bad_import = bool(
        re.search(r"^\s*(from|import)\s+(ff7_opcodes|field_maplist)\b",
                   response, re.M)
    )
    fact_ok = ("0x60" in response and "mapjump" in response.lower()) and (
        "0x2b" in response.lower() and "slip" in response.lower()
    ) if name == "opcode_byte_parsing" else True

    return {
        "exercise": name,
        "thinking_block_closed": thinking_ok,
        "self_contained": not bad_import,
        "opcode_facts_correct": fact_ok,
        "pass": thinking_ok and not bad_import and fact_ok,
    }


def main() -> int:
    exercises = build_exercises()
    results = []
    for ex in exercises:
        try:
            response = call_local_model(ex["prompt"])
        except NotImplementedError as e:
            print(f"[{ex['name']}] SKIPPED — {e}")
            continue
        result = evaluate(ex["name"], response)
        results.append(result)
        print(json.dumps(result, indent=2))

    if not results:
        print("\nNo exercises ran — wire up call_local_model() first.")
        return 1

    passed = sum(r["pass"] for r in results)
    print(f"\n{passed}/{len(results)} exercises passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
