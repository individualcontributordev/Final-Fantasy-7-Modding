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

DEFAULT_PROMPT = (
    "Walk this raw byte sequence from a field script block: "
    "60 01 00 00 00 00 00 00 00 00 2B 2B 48 00 01 02 03 04. "
    "Identify each opcode by its leading byte, and state its offset, name, "
    "and length in sequence. Do not use external imports."
)

SYSTEM_PROMPT = "You are an expert PlayStation 1 and Final Fantasy VII reverse engineering model."

ADAPTER_DIR = "ff7_coder_lora_model"


def main():
    user_query = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PROMPT

    print("🚀 Loading base model + adapter for greedy decode test...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="unsloth/DeepSeek-R1-Distill-Llama-8B",
        max_seq_length=4096,
        dtype=torch.float16,
        load_in_4bit=True,
    )
    model.load_adapter(ADAPTER_DIR)
    FastLanguageModel.for_inference(model)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([prompt], return_tensors="pt").to("cuda")
    input_length = inputs.input_ids.shape[-1]

    print(f"👤 Prompt: {user_query}\n")
    print("🤔 Generating with do_sample=False (greedy, deterministic)...")

    outputs = model.generate(
        input_ids=inputs.input_ids,
        attention_mask=inputs.attention_mask,
        max_new_tokens=512,
        do_sample=False,
        use_cache=True,
    )

    generated_tokens = outputs[0, input_length:]
    response_text = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

    print("\n🤖 Greedy response:\n")
    print(response_text)

    # Quick heuristic: count long stretches of alpha chars with no space,
    # which is the signature of the fused-word collapse we're diagnosing.
    import re
    long_fused_runs = re.findall(r"[A-Za-z]{25,}", response_text)
    print(f"\n📏 Diagnostic: {len(long_fused_runs)} fused-word run(s) of 25+ letters with no space.")
    if long_fused_runs:
        print("   Example run(s):", long_fused_runs[:3])
        print("   -> Collapse reproduces under greedy decoding: this points at the")
        print("      LoRA weights/training (overfit degeneracy), not sampling temp/top_p.")
    else:
        print("   -> No fused-word collapse under greedy decoding: sampling params")
        print("      (temperature/top_p in run_ff7_agent.py) are the likely cause.")


if __name__ == "__main__":
    main()
