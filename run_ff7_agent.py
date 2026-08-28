import warnings
import logging
import os
import sys
import contextlib
import io

# STEP 1: SILENCE NOISY HUGGINGFACE GENERATION WARNINGS BEFORE LOADING
warnings.filterwarnings("ignore")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("unsloth").setLevel(logging.ERROR)

import subprocess
import re
import time
import torch
from unsloth import FastLanguageModel

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
try:
    from rag_retrieve import retrieve as rag_retrieve, format_context as rag_format_context
    RAG_AVAILABLE = True
except Exception as _rag_import_err:
    RAG_AVAILABLE = False
    _rag_import_error_msg = str(_rag_import_err)

print("🚀 Booting your specialized FF7 Agent environment...")
start_boot = time.time()

# 2. Load the exact base student model cores
max_seq_length = 4096
dtype = torch.float16

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/DeepSeek-R1-Distill-Llama-8B",
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = True, # Kept active to protect your 8GB RTX 3070 VRAM footprint
)

# Load and attach your custom fine-tuned ChatML adapters directly on top!
print("🧠 Applying custom fine-tuned Final Fantasy VII adapters...")
model.load_adapter("ff7_coder_lora_model")
FastLanguageModel.for_inference(model)

print(f"✔ Specialized FF7 brain loaded natively into VRAM in {time.time() - start_boot:.2f} seconds.")

# 3. System Prompt Persona (Strictly matches train_ff7.py distribution to avoid token drift)
SYSTEM_PROMPT = "You are an expert PlayStation 1 and Final Fantasy VII reverse engineering model."

# 4. Human-In-The-Loop Execution Engine (Security Controls, Traversal Guard, Backups)
def execute_system_tool(model_output):
    # Robust match to handle cross-platform \r\n or trailing whitespaces inside code blocks
    bash_match = re.search(r"```bash\s*\n(.*?)\n```", model_output, re.DOTALL)
    if bash_match:
        command = bash_match.group(1).strip()
        print(f"\n⚠️  [AGENT REQUESTS BASH EXECUTION]:\n----------------------------------------\n{command}\n----------------------------------------")

        confirm = input("Confirm execution? [y/N]: ").strip().lower()
        if confirm != 'y':
            print("❌ Execution canceled by user.")
            return "ERROR: Bash command execution was rejected by the human operator."

        print(f"\n[RUNNING BASH]: {command}")
        start_tool = time.time()
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"⏱️ [TOOL TIME]: Bash execution completed in {time.time() - start_tool:.2f} seconds.")
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

    python_match = re.search(r"```python\s*\n(.*?)\n```", model_output, re.DOTALL)
    if python_match:
        code = python_match.group(1).strip()
        filename = "temp_patch.py"
        file_target = re.search(r"# TARGET_FILE:\s*(\S+)", code)
        if file_target:
            filename = file_target.group(1)

        # Path Confinement Guard: Flatten traversal attempts to protect local directories
        filename = os.path.basename(filename)

        print(f"\n⚠️  [AGENT REQUESTS FILE WRITE]: {filename}")
        if os.path.exists(filename):
            print(f"🚨 WARNING: '{filename}' already exists in this directory and will be overwritten!")

        confirm = input("Confirm write operation? [y/N]: ").strip().lower()
        if confirm != 'y':
            print("❌ File write operation canceled by user.")
            return "ERROR: File modification script execution was rejected by the human operator."

        # DISASTER RECOVERY SAFEGUARD: Auto-generate a pristine .bak copy before any rewrite
        if os.path.exists(filename) and not os.path.exists(filename + ".bak"):
            import shutil
            try:
                shutil.copy2(filename, filename + ".bak")
                print(f"📦 [SAFEGUARD]: Successfully backed up existing file to {filename}.bak")
            except Exception as backup_error:
                print(f"⚠️ Backup operation failed: {backup_error}. Aborting write for workspace safety.")
                return f"ERROR: System tool could not create file backup safeguard: {backup_error}"

        print(f"\n[AGENT WRITING FILE]: {filename}")
        start_tool = time.time()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"⏱️ [TOOL TIME]: File written in {time.time() - start_tool:.3f} seconds.")
        return f"Successfully wrote script to file path: {filename}"

    return None

print("\n🤖 ==================================================================== 🤖")
print("🤖 Custom FF7 Autonomous Agent Active and Armed. (Type 'exit' to quit)   🤖")
print("🤖 ==================================================================== 🤖")

chat_history = []
TRIGGER_COMMANDS = ["!confirm", "!works", "!verify", "!save"]

# 5. Interactive Persistent Shell Loop
while True:
    try:
        user_query = input("\n👤 User: ").strip()
        if not user_query: continue
        if user_query.lower() in ['exit', 'quit']:
            print("Shutting down agent loop. Goodbye!")
            break

        # BACKGROUND AUTOMATION ENGINE: Organic growth dataset compiler
        if any(user_query.lower().startswith(cmd) for cmd in TRIGGER_COMMANDS):
            user_turns = [text for role, text in chat_history if role == "user"]
            agent_turns = [text for role, text in chat_history if role == "assistant"]
            if user_turns and agent_turns:
                print("\n⚡ [AUTOMATION]: Harvesting successful workspace parameters...")
                start_auto = time.time()
                last_problem = user_turns[-1]
                last_solution = agent_turns[-1]

                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Format this into a single-line training JSON object:\nPROBLEM: {last_problem}\nSOLUTION: {last_solution}"}
                ]
                ext_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                ext_inputs = tokenizer([ext_prompt], return_tensors="pt").to("cuda")

                with contextlib.redirect_stderr(io.StringIO()):
                    ext_outputs = model.generate(input_ids=ext_inputs.input_ids, max_new_tokens=1024, use_cache=True)

                new_tokens = ext_outputs[0, ext_inputs.input_ids.shape[-1]:]
                raw_json = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
                try:
                    clean_json = re.sub(r"^```json\s*|\s*```$", "", raw_json.strip(), flags=re.MULTILINE)
                    os.makedirs("data", exist_ok=True)
                    with open("data/organic_growth.jsonl", "a", encoding="utf-8") as f:
                        f.write(clean_json.strip() + "\n")
                    print("🎉 [SUCCESS]: Dataset expanded organically via command override!")
                except Exception as e:
                    print(f"⚠️ Dataset append skipped: {e}")
            else:
                print("❌ [AUTOMATION]: No conversation history found in this session to harvest yet.")
            continue

        # --- RAG: GROUND THE QUERY IN VENDORED RE SOURCE REPOS (if index exists) ---
        rag_context = ""
        if RAG_AVAILABLE:
            try:
                rag_hits = rag_retrieve(user_query, top_k=4)
                rag_context = rag_format_context(rag_hits)
                if rag_hits:
                    print(f"📚 [RAG]: Retrieved {len(rag_hits)} grounding chunk(s) "
                          f"from {', '.join(sorted(set(h['source'] for h in rag_hits)))}")
            except FileNotFoundError:
                pass  # No index built yet — proceed ungrounded.
            except Exception as rag_err:
                print(f"⚠️ [RAG]: Retrieval skipped due to error: {rag_err}")

        # --- NATIVE CHATML RUNTIME INFERENCE PASS ---
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for role, text in chat_history[-4:]:
            if role in ["user", "assistant"]:
                messages.append({"role": role, "content": text})
        if rag_context:
            messages.append({
                "role": "user",
                "content": (
                    "Reference material retrieved from local reverse-engineering "
                    "source repos (cite file:line when you use these):\n\n"
                    f"{rag_context}"
                ),
            })
        messages.append({"role": "user", "content": user_query})

        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer([prompt], return_tensors="pt").to("cuda")
        input_length = inputs.input_ids.shape[-1]

        print("🤔 [AGENT]: Processing tokens and thinking on RTX 3070...")
        start_inference = time.time()

        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            outputs = model.generate(
                input_ids=inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=512,
                temperature=0.6,
                top_p=0.95,
                use_cache=True
            )

        elapsed_inference = time.time() - start_inference

        # Decode the output safely by indexing the batch row first
        generated_tokens = outputs[0, input_length:]
        response_text = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

        # Cleanly strip leading DeepSeek internal reasoning traces to prevent terminal leakage
        response_text = re.sub(r"^.*?<\/think>\s*", "", response_text, flags=re.DOTALL).strip()

        print(f"\n🤖 Agent:\n{response_text}")
        print(f"⏱️ [INFERENCE TIME]: Agent response generated in {elapsed_inference:.2f} seconds.")

        chat_history.append(("user", user_query))
        chat_history.append(("assistant", response_text))

        # Check for code block structures to trigger tools securely
        tool_output = execute_system_tool(response_text)
        if tool_output:
            print(f"\n💻 System Tool Output:\n{tool_output}")
            chat_history.append(("system", tool_output))

    except KeyboardInterrupt:
        continue
    except Exception as e:
        print(f"\nRuntime Error: {e}")
        break
