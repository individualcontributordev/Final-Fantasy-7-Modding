
import os
import torch
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# 1. Configuration Settings for 8GB VRAM
max_seq_length = 4096       # Safely handles longer hex structures and tables
dtype = torch.float16       # Explicitly forces Float16 optimization for the RTX 3070
load_in_4bit = True         # Uses 4-bit QLoRA to keep VRAM usage around ~5.2 GB

# 2. Load the DeepSeek-R1 8B Student Model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/DeepSeek-R1-Distill-Llama-8B",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# 3. Setup LoRA Weights targeting all core linear layers
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth", # Crucial VRAM saver for 8GB cards
    random_state = 3407,
)

# 4. Prompt Formatting Wrapper
def format_prompts(batch):
    instructions = batch["instruction"]
    inputs       = batch["input"]
    outputs      = batch["output"]
    texts = []
    for instruction, input_data, output in zip(instructions, inputs, outputs):
        text = f"### System:\nYou are an expert PlayStation 1 and Final Fantasy VII reverse engineering model.\n\n### Instruction:\n{instruction}\n\n### Input:\n{input_data}\n\n### Response:\n{output}"
        texts.append(text)
    return { "text" : texts }

# Load your 1,348 rows compiled by Auggie
dataset_path = "data/ff7_re_dataset.jsonl" 
dataset = load_dataset("json", data_files=dataset_path, split="train")
dataset = dataset.map(format_prompts, batched=True)

# 5. Training Hyperparameters tuned for 1,348 rows on an RTX 3070
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    packing = True, # Packs smaller opcode instructions together to minimize overhead
    args = TrainingArguments(
        per_device_train_batch_size = 2,    # Set to 2 to prevent VRAM spikes on 8GB cards
        gradient_accumulation_steps = 4,    # Results in a stable effective batch size of 8
        warmup_steps = 10,
        max_steps = 200,                    # Balanced steps for a solid initial learning curve
        learning_rate = 2e-4,
        fp16 = True,                        # Explicitly enables Ampere Float16 acceleration
        bf16 = False,
        logging_steps = 1,
        optim = "adamw_8bit",               # Uses the 8-bit optimizer to save ~1.5 GB of VRAM
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "ff7_coder_outputs",
    ),
)

# 6. Execute Fine-Tuning Execution Run
print("🚀 Launching execution matrix on NVIDIA GeForce RTX 3070...")
trainer_stats = trainer.train()
print("✔ Training cycle completed!")

# 7. Save the Weight Adapters Locally
model.save_pretrained("ff7_coder_lora_model")
tokenizer.save_pretrained("ff7_coder_lora_model")
print("🎉 LoRA parameters successfully saved to './ff7_coder_lora_model'!")
