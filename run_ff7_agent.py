# TARGET_FILE: run_ff7_agent.py
import os
import subprocess
import re
from unsloth import FastLanguageModel
import torch

print("🚀 Booting your specialized FF7 Agent environment...")

# 1. Initialize Your Highly Specialized Fine-Tuned Brain
max_seq_length = 4096
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/DeepSeek-R1-Distill-Llama-8B", 
    max_seq_length = max_seq_length,
    dtype = torch.float16,
    load_in_4bit = True, 
)
model.load_adapter("ff7_coder_lora_model")
FastLanguageModel.for_inference(model)

# 2. System Context
WORKSPACE_CONTEXT = """
You are an autonomous Agentic Terminal Engine. You operate natively on the user's workstation.
📍 HARDCODED WORKSPACE DIRECTORY MAP:
- Notes/Logs: /mnt/d/Final-Fantasy-7-CSR, /mnt/d/projects/Final-Fantasy-7-Modding
- Workspace:  /mnt/d/projects/Final-Fantasy-7-Modding/workspace
- Web App:    /mnt/d/individualcontributordev.github.io
- References: /mnt/d/makoureactor, /mnt/d/ff7tk, /mnt/d/Downloads/ghidra_12.1.2_PUBLIC
"""

# 3. Native Execution Engine (The "Hands")
def execute_system_tool(model_output):
    bash_match = re.search(r"```bash\n(.*?)\n```", model_output, re.DOTALL)
    if bash_match:
        command = bash_match.group(1).strip()
        print(f"\n[AGENT BASH EXECUTION]: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

    python_match = re.search(r"```python\n(.*?)\n```", model_output, re.DOTALL)
    if python_match:
        code = python_match.group(1).strip()
        filename = "temp_patch.py"
        file_target = re.search(r"# TARGET_FILE:\s*(\S+)", code)
        if file_target: filename = file_target.group(1)
        print(f"\n[AGENT WRITING FILE]: {filename}")
        with open(filename, "w", encoding="utf-8") as f: f.write(code)
        return f"Successfully wrote script to file path: {filename}"
    return None

# 4. Interactive Conversational Loop & Automatic Dataset Harvester
print("\n🤖 ==================================================================== 🤖")
print("🤖 Custom FF7 Autonomous Agent Active and Armed. (Type 'exit' to quit)   🤖")
print("🤖 ==================================================================== 🤖")

chat_history = []
TRIGGER_KEYWORDS = ["confirm", "it works", "verified", "working code"]

# Force an infinite input collection pass
while True:
    try:
        # Prompt the user for input explicitly
        user_query = input("\n👤 User: ").strip()
        
        # Guard clause against empty return keys
        if not user_query:
            continue
            
        if user_query.lower() in ['exit', 'quit']:
            print("Shutting down agent loop. Goodbye!")
            break

        # BACKGROUND AUTOMATION ENGINE: Check for success validation triggers
        if any(keyword in user_query.lower() for keyword in TRIGGER_KEYWORDS) and len(chat_history) >= 2:
            print("\n⚡ [AUTOMATION]: Compiling this success into your dataset in the background...")
            last_problem = chat_history[-2][1]
            last_solution = chat_history[-1][1]
            
            silent_prompt = f"### System:\nFormat this interaction into a single-line JSON training row matching our structural schema: {{\"instruction\": \"...\", \"input\": \"...\", \"output\": \"<thinking>...</thinking>...\"}}\n\nPROBLEM: {last_problem}\nSOLUTION: {last_solution}\n\n### Response:\n"
            ext_inputs = tokenizer([silent_prompt], return_tensors="pt").to("cuda")
            ext_outputs = model.generate(input_ids=ext_inputs.input_ids, max_new_tokens=1024, use_cache=True)
            raw_json = tokenizer.batch_decode(ext_outputs).split("### Response:\n")[-1].replace("</s>", "").strip()
            
            try:
                clean_json = re.sub(r"^```json\s*|\s*```$", "", raw_json.strip(), flags=re.MULTILINE)
                with open("data/organic_growth.jsonl", "a", encoding="utf-8") as f:
                    f.write(clean_json.strip() + "\n")
                print("🎉 [SUCCESS]: Ground-truth row appended to data/organic_growth.jsonl!")
            except Exception as e:
                print(f"⚠️ Dataset append skipped: {e}")
                
            chat_history.append(("User", user_query))
            continue

        # STANDARD GENERATION ENGINE
        prompt = f"### System:\n{WORKSPACE_CONTEXT}\n\n"
        for role, text in chat_history[-4:]:
            prompt += f"### {role}:\n{text}\n\n"
        prompt += f"### Instruction:\n{user_query}\n\n### Response:\n"
        
        inputs = tokenizer([prompt], return_tensors="pt").to("cuda")
        outputs = model.generate(input_ids=inputs.input_ids, max_new_tokens=1024, use_cache=True)
        response_text = tokenizer.batch_decode(outputs).split("### Response:\n")[-1].replace("</s>", "").strip()
        
        print(f"\n🤖 Agent:\n{response_text}")
        chat_history.append(("User", user_query))
        chat_history.append(("Agent", response_text))

        # Check for tool/code execution commands
        tool_output = execute_system_tool(response_text)
        if tool_output:
            print(f"\n💻 System Tool Output:\n{tool_output}")
            chat_history.append(("System", tool_output))

    except KeyboardInterrupt:
        print("\nSession interrupted via keyboard. Type 'exit' to shut down safely.")
        continue
    except Exception as e:
        print(f"\nRuntime Error: {e}")
        break
