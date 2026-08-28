import os
import sys
import torch
import warnings
import logging
import re
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer

# Force complete warning and telemetry suppression
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("unsloth").setLevel(logging.ERROR)

# ====================================================================
# 1. HARDWARE SETTINGS (Optimized for RTX 3070 8GB VRAM)
# ====================================================================
max_seq_length = 4096
dtype = torch.float16
load_in_4bit = True

# ====================================================================
# 2. LOAD DEEPSEEK STUDENT MODEL CORES
# ====================================================================
print("🚀 Loading DeepSeek-R1 8B Model into 4-bit VRAM...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/DeepSeek-R1-Distill-Llama-8B",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# ====================================================================
# 3. CONFIGURE TARGET LORA MODULES
# ====================================================================
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
)

# ====================================================================
# 4. PROMPT FORMATTING ENGINE (Uses Native Tokenizer Template)
# ====================================================================
def format_prompts(batch):
    instructions = batch["instruction"]
    inputs       = batch["input"]
    outputs      = batch["output"]
    texts = []

    for instruction, input_data, output in zip(instructions, inputs, outputs):
        user_content = f"{instruction}\n\nInput Context:\n{input_data}" if input_data else instruction

        # Structured with strict ChatML keys and full system persona conditioning
        messages = [
            {"role": "system", "content": "You are an expert PlayStation 1 and Final Fantasy VII reverse engineering model."},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": output}
        ]

        # Apply the tokenizer's built-in chat template natively to preserve special tokens
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
        texts.append(text)

    return { "text" : texts }

print("📦 Mapping your master dataset rows into formatting engine...")
dataset_path = "data/ff7_re_dataset.jsonl"
dataset = load_dataset("json", data_files=dataset_path, split="train")
dataset = dataset.map(format_prompts, batched=True)

# ====================================================================
# 5. CONFIGURATION WRAPPER RESOLUTION (Protects against TRL Deprecations)
# ====================================================================
try:
    from trl import SFTConfig
    print("📋 Testing modern SFTConfig parameter structure compilation...")

    training_args = SFTConfig(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 10,
        max_steps = 200,
        learning_rate = 2e-4,
        fp16 = True,
        bf16 = False,
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "ff7_coder_outputs",
        dataset_text_field = "text",
        max_seq_length = max_seq_length,
        packing = True,
    )

    # Try initializing SFTTrainer with modern processing_class logic
    try:
        trainer = SFTTrainer(
            model = model,
            processing_class = tokenizer,
            train_dataset = dataset,
            args = training_args,
        )
    except TypeError:
        # Fallback to standard tokenizer parameter if on a transitional TRL version
        trainer = SFTTrainer(
            model = model,
            tokenizer = tokenizer,
            train_dataset = dataset,
            args = training_args,
        )

except Exception as e:
    from transformers import TrainingArguments
    print(f"📋 Falling back to legacy TRL direct Trainer kwargs. Notice: {e}")

    training_args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 10,
        max_steps = 200,
        learning_rate = 2e-4,
        fp16 = True,
        bf16 = False,
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "ff7_coder_outputs",
    )

    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = dataset,
        dataset_text_field = "text",
        max_seq_length = max_seq_length,
        packing = True,
        args = training_args,
    )

# ====================================================================
# 6. EXECUTE FINE-TUNING ENGINES
# ====================================================================
print("🚀 Launching execution matrix on NVIDIA GeForce RTX 3070...")
trainer.train()
print("✔ Training cycle completed successfully!")

# Save our fresh weight adapters directly to our local project folder
model.save_pretrained("ff7_coder_lora_model")
tokenizer.save_pretrained("ff7_coder_lora_model")
print("🎉 LoRA parameters successfully saved to './ff7_coder_lora_model'!")
