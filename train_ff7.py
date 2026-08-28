import os
import sys
import torch
import warnings
import logging
import re

# ====================================================================
# -1. MINIMAL .env LOADER (no python-dotenv dependency; must run first so
#     HF_TOKEN / HF_HOME / HF_HUB_* are set before huggingface_hub reads them)
# ====================================================================
def _load_dotenv(path=".env"):
    if not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value

_load_dotenv()

# ====================================================================
# 0. FUSED CROSS-ENTROPY MEMORY-PROBE WORKAROUND (must run before unsloth import)
# ====================================================================
# unsloth_zoo's fused CE loss picks a chunk size by measuring free VRAM at the
# instant compute_loss runs. On 8GB cards, headroom at that point can round to
# ~0 free GB, causing a crash: "Unsloth: No or negligible GPU memory available
# for fused cross entropy." (unslothai/unsloth#3827). Forcing a fixed chunk
# count bypasses that live memory probe entirely.
os.environ.setdefault("UNSLOTH_CE_LOSS_N_CHUNKS", "8")

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
max_seq_length = 1536
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

# ---------------------------------------------------------------------
# TOKENIZER FIX (huggingface/transformers#45488): transformers v5's
# LlamaTokenizer.__init__ unconditionally overwrites tokenizer.json's real
# ByteLevel pre_tokenizer/decoder with a hardcoded SentencePiece-style
# Metaspace pipeline. This model's vocab has zero "▁"-prefixed tokens, so
# Metaspace silently drops every space during encode, producing fused-word
# training data. Patch it by loading the raw tokenizers.Tokenizer (which
# parses tokenizer.json directly, bypassing LlamaTokenizer's override) and
# copying its correct pre_tokenizer/decoder onto the loaded tokenizer.
from tokenizers import Tokenizer as _RawTokenizer
_raw_tok = _RawTokenizer.from_pretrained("unsloth/DeepSeek-R1-Distill-Llama-8B")
tokenizer.backend_tokenizer.pre_tokenizer = _raw_tok.pre_tokenizer
tokenizer.backend_tokenizer.decoder = _raw_tok.decoder
_probe_ids = tokenizer("You are an expert", add_special_tokens=False).input_ids
assert tokenizer.decode(_probe_ids) == "You are an expert", (
    "Tokenizer pre_tokenizer/decoder patch failed -- fused-word bug still present!"
)
print("✅ Tokenizer pre_tokenizer/decoder patched (ByteLevel restored, Metaspace bug fixed).")

# ====================================================================
# 3. CONFIGURE TARGET LORA MODULES
# ====================================================================
model = FastLanguageModel.get_peft_model(
    model,
    r = 8,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 8,
    lora_dropout = 0.05,
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

# Hold out 10% as an eval split so we can see eval_loss (memorization vs.
# generalization) instead of flying blind on train_loss alone.
dataset = dataset.train_test_split(test_size=0.1, seed=3407)
train_dataset = dataset["train"]
eval_dataset = dataset["test"]
print(f"📊 Split dataset: {len(train_dataset)} train / {len(eval_dataset)} eval rows.")

# ====================================================================
# 5. CONFIGURATION WRAPPER RESOLUTION (Protects against TRL Deprecations)
# ====================================================================
try:
    from trl import SFTConfig
    print("📋 Testing modern SFTConfig parameter structure compilation...")

    training_args = SFTConfig(
        per_device_train_batch_size = 1,
        per_device_eval_batch_size = 1,
        gradient_accumulation_steps = 8,
        warmup_steps = 10,
        max_steps = 90,
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
        eval_strategy = "steps",
        eval_steps = 10,
        save_strategy = "steps",
        save_steps = 10,
        save_total_limit = 3,
        load_best_model_at_end = True,
        metric_for_best_model = "eval_loss",
        greater_is_better = False,
    )

    # Try initializing SFTTrainer with modern processing_class logic
    try:
        trainer = SFTTrainer(
            model = model,
            processing_class = tokenizer,
            train_dataset = train_dataset,
            eval_dataset = eval_dataset,
            args = training_args,
        )
    except TypeError:
        # Fallback to standard tokenizer parameter if on a transitional TRL version
        trainer = SFTTrainer(
            model = model,
            tokenizer = tokenizer,
            train_dataset = train_dataset,
            eval_dataset = eval_dataset,
            args = training_args,
        )

except Exception as e:
    from transformers import TrainingArguments
    print(f"📋 Falling back to legacy TRL direct Trainer kwargs. Notice: {e}")

    training_args = TrainingArguments(
        per_device_train_batch_size = 1,
        per_device_eval_batch_size = 1,
        gradient_accumulation_steps = 8,
        warmup_steps = 10,
        max_steps = 90,
        learning_rate = 2e-4,
        fp16 = True,
        bf16 = False,
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "ff7_coder_outputs",
        eval_strategy = "steps",
        eval_steps = 10,
        save_strategy = "steps",
        save_steps = 10,
        save_total_limit = 3,
        load_best_model_at_end = True,
        metric_for_best_model = "eval_loss",
        greater_is_better = False,
    )

    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = train_dataset,
        eval_dataset = eval_dataset,
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
