"""
Checks whether format_prompts()'s chat-template application, followed by a
tokenize/decode round-trip, introduces the fused-word collapse -- i.e. does
the ENCODE side (not the already-cleared decode side) lose inter-word space
tokens before training ever sees the data?

Run on the workstation (needs transformers/unsloth installed):
    python3 check_format_tokenize.py
"""
import json
import re
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("unsloth/DeepSeek-R1-Distill-Llama-8B")

# Pinpoint whether ENCODE or DECODE is dropping space markers, using a tiny
# known-good sentence with no model/dataset involved at all.
probe = "You are an expert PlayStation 1 and Final Fantasy VII reverse engineering model."
probe_ids = tokenizer(probe, add_special_tokens=False).input_ids
probe_tokens = tokenizer.convert_ids_to_tokens(probe_ids)
print("=== ENCODE/DECODE PROBE ===")
print("Input string:", repr(probe))
print("Token strings (first 20):", probe_tokens[:20])
print("Decoded (default):", repr(tokenizer.decode(probe_ids, skip_special_tokens=True)))
print("Decoded (clean_up_tokenization_spaces=False):",
      repr(tokenizer.decode(probe_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)))
print("Manual Ġ/Ċ join:", repr("".join(probe_tokens).replace("\u0120", " ").replace("\u010a", "\n")))
try:
    print("backend decoder type:", type(tokenizer.backend_tokenizer.decoder))
except Exception as e:
    print("backend decoder introspection failed:", e)
print("============================\n")

SYSTEM_PROMPT = "You are an expert PlayStation 1 and Final Fantasy VII reverse engineering model."

fused_in_formatted_text = 0
fused_after_roundtrip = 0
examples_formatted = []
examples_roundtrip = []

with open("data/ff7_re_dataset.jsonl") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    d = json.loads(line)
    instruction = d.get("instruction", "")
    input_data = d.get("input", "")
    output = d.get("output", "")
    user_content = f"{instruction}\n\nInput Context:\n{input_data}" if input_data else instruction

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
        {"role": "assistant", "content": output},
    ]

    # Step 1: chat template application (same as format_prompts in train_ff7.py)
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    runs = re.findall(r"[A-Za-z]{25,}", text)
    if runs:
        fused_in_formatted_text += len(runs)
        if len(examples_formatted) < 5:
            examples_formatted.append((i, runs[:3]))

    # Step 2: tokenize then decode -- does the encode/decode round trip itself
    # eat space tokens that were present in `text`?
    ids = tokenizer(text, add_special_tokens=False).input_ids
    roundtrip = tokenizer.decode(ids, skip_special_tokens=True)
    rt_runs = re.findall(r"[A-Za-z]{25,}", roundtrip)
    if rt_runs:
        fused_after_roundtrip += len(rt_runs)
        if len(examples_roundtrip) < 5:
            examples_roundtrip.append((i, rt_runs[:3]))

print(f"Rows checked: {len(lines)}")
print(f"Fused runs in chat-template-formatted text (pre-tokenize): {fused_in_formatted_text}")
for e in examples_formatted:
    print("  ", e)
print(f"Fused runs after tokenize->decode round trip: {fused_after_roundtrip}")
for e in examples_roundtrip:
    print("  ", e)

if fused_in_formatted_text == 0 and fused_after_roundtrip == 0:
    print("\n-> Chat template + tokenize/decode round trip is clean.")
    print("   The pathology is not in data formatting or tokenization -- it is")
    print("   specific to autoregressive GENERATION (the model's learned")
    print("   next-token distribution), pointing back at training dynamics")
    print("   (e.g. packing without proper sequence boundaries, or LoRA rank")
    print("   still insufficient) rather than a data/tokenizer bug.")
elif fused_in_formatted_text > 0:
    print("\n-> Chat template application itself is introducing fused words.")
    print("   Check tokenizer_config.json's chat_template for whitespace-eating")
    print("   Jinja control (e.g. '{%-' / '-%}') around message content blocks.")
else:
    print("\n-> Formatted text is clean but tokenize->decode round trip fuses words.")
    print("   This points at a tokenizer encode/decode inconsistency independent")
    print("   of generation.")
