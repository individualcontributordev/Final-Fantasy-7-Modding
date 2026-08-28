"""
Standalone greedy-decoding sanity check for the current LoRA adapter.

Purpose: isolate whether the whitespace-collapsed/garbled generation seen in
run_ff7_agent.py (temperature=0.6, top_p=0.95) is a *sampling* artifact or a
property of the trained weights themselves. Greedy decoding (do_sample=False)
is deterministic and picks the single highest-probability token at each step
-- if the collapse still happens here, it confirms the degeneracy lives in
the LoRA weights/training, not in temperature/top_p sampling noise.

Usage:
    python3 eval_greedy_test.py
    python3 eval_greedy_test.py "Some other prompt to test"
"""
import os
import sys
import warnings
import logging

warnings.filterwarnings("ignore")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("unsloth").setLevel(logging.ERROR)

import torch
from unsloth import FastLanguageModel

OOD_PROMPT = (
    "Walk this raw byte sequence from a field script block: "
    "60 01 00 00 00 00 00 00 00 00 2B 2B 48 00 01 02 03 04. "
    "Identify each opcode by its leading byte, and state its offset, name, "
    "and length in sequence. Do not use external imports."
)

IN_DISTRIBUTION_PROMPT = (
    "What are the instruction lengths of PMVIE (0xF8) and MOVIE (0xF9), "
    "and why does PMVIE need an operand while MOVIE doesn't?"
)

# Thin-bucket probes (ISO/Mode2/burning, Ghidra/MIPS, LZS/GZIPPS compression) --
# added after auditing bucket sizes (33/22/21 rows vs. 1000+ for opcode/CSR).
ISO_MODE2_PROMPT_1 = (
    "ImgBurn reports a verify failure at a given LBA/offset inside a raw "
    "MODE2/2352 sector, but the user-data bytes are byte-identical to a "
    "pristine reference image. What field is most likely at fault, and why "
    "would a real PS1/PS2 drive still play the disc fine despite the verify "
    "failure?"
)
ISO_MODE2_PROMPT_2 = (
    "psx_mode2_iso.py's replace_file_padded refuses to grow a file by only a "
    "few bytes even though ceil(old_size/2048) == ceil(new_size/2048). What "
    "ISO9660 fields actually need updating to allow this, and why was the "
    "original check wrong?"
)
GHIDRA_PROMPT_1 = (
    "I imported FIELD.BIN into Ghidra at base address 0x80000000 and none of "
    "my known function addresses from prior notes line up. What's wrong, and "
    "what correction do I need to apply to every address I look up?"
)
GHIDRA_PROMPT_2 = (
    "In a Ghidra decompile of a PS1 kernel executable, I see a function "
    "reading MOVIE_ID.BIN into a fixed buffer but never indexing it by movie "
    "id. What does this tell me about where a per-movie hardcoded behavior "
    "(like a fixed LBA seek) is more likely to live instead?"
)
COMPRESSION_PROMPT_1 = (
    "Describe the LZS ring buffer used by this engine's field/movie "
    "compression: its size, initial fill position, and how match "
    "offset/length are packed into the 2-byte control encoding."
)
COMPRESSION_PROMPT_2 = (
    "Why can a hash-chain LZS encoder produce a stream that decompresses "
    "correctly on PC tools but corrupts on real PS1 hardware, even though "
    "the compressed bytes are technically valid per the format spec?"
)

SYSTEM_PROMPT = "You are an expert PlayStation 1 and Final Fantasy VII reverse engineering model."

ADAPTER_DIR = "ff7_coder_lora_model"


def run_prompt(model, tokenizer, label, user_query):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([prompt], return_tensors="pt").to("cuda")
    input_length = inputs.input_ids.shape[-1]

    print(f"\n{'=' * 70}")
    print(f"[{label}]")
    print(f"👤 Prompt: {user_query}\n")
    print("🤔 Generating with do_sample=False + repetition_penalty=1.3, "
          "no_repeat_ngram_size=4 (deterministic, loop-blocked)...")

    outputs = model.generate(
        input_ids=inputs.input_ids,
        attention_mask=inputs.attention_mask,
        max_new_tokens=512,
        do_sample=False,
        repetition_penalty=1.3,
        no_repeat_ngram_size=4,
        use_cache=True,
    )

    generated_tokens = outputs[0, input_length:]
    response_text = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

    print("\n🤖 Response:\n")
    print(response_text)

    # Diagnostic: check whether literal byte-level BPE markers (Ġ=space,
    # Ċ=newline) leaked into the decoded string undconverted. If so, this
    # points at a tokenizer.decode() byte-reassembly bug rather than (or in
    # addition to) a weights/training problem -- try a manual raw-token
    # reconstruction as a cross-check.
    if "Ġ" in response_text or "Ċ" in response_text:
        print("\n⚠️  Literal byte-level BPE markers (Ġ/Ċ) found in decoded text -- "
              "possible tokenizer.decode() bug, not just a weights issue.")
        raw_tokens = tokenizer.convert_ids_to_tokens(generated_tokens)
        manual_text = "".join(raw_tokens).replace("Ġ", " ").replace("Ċ", "\n")
        print("\n🔧 Manual raw-token reconstruction (Ġ->space, Ċ->newline):\n")
        print(manual_text)

    import re
    long_fused_runs = re.findall(r"[A-Za-z]{25,}", response_text)
    print(f"\n📏 Diagnostic: {len(long_fused_runs)} fused-word run(s) of 25+ letters with no space.")
    if long_fused_runs:
        print("   Example run(s):", long_fused_runs[:3])
        print("   -> Fused-word collapse still present -> weights/training issue.")
    else:
        print("   -> No fused-word collapse.")

    # Detect degenerate repetition loops (e.g. "60 0x 60 0x ..." repeating).
    tokens = response_text.split()
    if len(tokens) >= 12:
        window = 4
        repeats = 0
        for i in range(len(tokens) - window):
            if tokens[i:i + window] == tokens[i + window:i + 2 * window]:
                repeats += 1
        if repeats > 3:
            print(f"   -> Repetition-loop diagnostic: {repeats} repeated {window}-token windows detected.")
        else:
            print("   -> No repetition-loop pattern detected.")


def main():
    custom_prompt = sys.argv[1] if len(sys.argv) > 1 else None

    print("🚀 Loading base model + adapter for greedy decode test...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="unsloth/DeepSeek-R1-Distill-Llama-8B",
        max_seq_length=4096,
        dtype=torch.float16,
        load_in_4bit=True,
    )
    model.load_adapter(ADAPTER_DIR)
    FastLanguageModel.for_inference(model)

    # TOKENIZER FIX (huggingface/transformers#45488): see train_ff7.py for
    # full explanation. transformers v5's LlamaTokenizer.__init__ overwrites
    # tokenizer.json's real ByteLevel pre_tokenizer/decoder with a broken
    # Metaspace pipeline, causing every space to be dropped during encode.
    from tokenizers import Tokenizer as _RawTokenizer
    _raw_tok = _RawTokenizer.from_pretrained("unsloth/DeepSeek-R1-Distill-Llama-8B")
    tokenizer.backend_tokenizer.pre_tokenizer = _raw_tok.pre_tokenizer
    tokenizer.backend_tokenizer.decoder = _raw_tok.decoder
    _probe_ids = tokenizer("You are an expert", add_special_tokens=False).input_ids
    assert tokenizer.decode(_probe_ids) == "You are an expert", (
        "Tokenizer pre_tokenizer/decoder patch failed -- fused-word bug still present!"
    )
    print("✅ Tokenizer pre_tokenizer/decoder patched (ByteLevel restored, Metaspace bug fixed).")

    if custom_prompt:
        run_prompt(model, tokenizer, "CUSTOM", custom_prompt)
    else:
        run_prompt(model, tokenizer, "IN-DISTRIBUTION (PMVIE/MOVIE length)", IN_DISTRIBUTION_PROMPT)
        run_prompt(model, tokenizer, "OUT-OF-DISTRIBUTION (byte-walk)", OOD_PROMPT)
        run_prompt(model, tokenizer, "ISO/MODE2 (EDC verify-fail triage)", ISO_MODE2_PROMPT_1)
        run_prompt(model, tokenizer, "ISO/MODE2 (directory-record growth)", ISO_MODE2_PROMPT_2)
        run_prompt(model, tokenizer, "GHIDRA (FIELD.BIN base address)", GHIDRA_PROMPT_1)
        run_prompt(model, tokenizer, "GHIDRA (hardcode localization reasoning)", GHIDRA_PROMPT_2)
        run_prompt(model, tokenizer, "COMPRESSION (LZS ring buffer)", COMPRESSION_PROMPT_1)
        run_prompt(model, tokenizer, "COMPRESSION (hash-chain encoder hazard)", COMPRESSION_PROMPT_2)


if __name__ == "__main__":
    main()
