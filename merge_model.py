# TARGET_FILE: merge_model.py
from unsloth import FastLanguageModel
import torch

print("Merging LoRA adapters into a single 16-bit standalone matrix...")

# 1. Load the exact base model and your fresh adapters
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "ff7_coder_lora_model", 
    max_seq_length = 4096,
    dtype = torch.float16,
    load_in_4bit = False, # Must be False to cleanly merge full 16-bit float matrices
)

# 2. Export the merged weights directly into a single standalone directory
model.save_pretrained_merged(
    "ff7_coder_complete_agent", 
    tokenizer, 
    save_method = "merged_16bit"
)

print("🎉 Success! Your complete standalone agent brain is saved at './ff7_coder_complete_agent'")
print("You can now run 'run_ff7_agent.py' pointing directly to this merged directory!")
